import asyncio

from zmq import ZMQError, Poller, POLLIN


class MessagePool:
    def __init__(self):
        self.pool = {}
        self.curr_id = 0

    def add(self, message):
        self.curr_id += 1
        self.pool[self.curr_id] = message
        return self.curr_id

    def get(self, id):
        return self.pool.get(id, None)

    def remove(self, id):
        if id in self.pool:
            del self.pool[id]

    def cleanup(self, id, topic, queues):
        # discard message if depleted
        depleted = True
        for subbed_topics in queues.get_subbed_topics():
            if topic not in subbed_topics.keys():
                continue
            if id in subbed_topics[topic]:
                depleted = False
                break
        if depleted:
            self.remove(id)


class MessageQueues:
    def __init__(self):
        self.queues = {}

    def get_subbed_topics(self):
        return self.queues.values()

    def add(self, sub, topic, message_id):
        # add new subscriber queue
        if sub not in self.queues.keys():
            self.queues[sub] = {}
        # add new topic queue
        if topic not in self.queues[sub].keys():
            self.queues[sub][topic] = []
        # add to existent queue
        self.queues[sub][topic].append(message_id)

    def remove(self, sub, topic):
        # nothing to remove
        if sub not in self.queues.keys() or topic not in self.queues[sub].keys():
            return
        del self.queues[sub][topic]

    def pop(self, sub, topic):
        # nothing to pop
        if sub not in self.queues.keys() or topic not in self.queues[sub].keys() or len(self.queues[sub][topic]) == 0:
            return None
        return self.queues[sub][topic].pop(0)

    def peek(self, sub, topic):
        if sub not in self.queues.keys() or topic not in self.queues[sub].keys() or len(self.queues[sub][topic]) == 0:
            return None
        return self.queues[sub][topic][0]

    def get_all(self, sub, topic):
        # nothing to get
        if sub not in self.queues.keys() or topic not in self.queues[sub].keys() or len(self.queues[sub][topic]) == 0:
            return
        return self.queues[sub][topic]


class Subscriptions:
    def __init__(self):
        self.subs = {}

    def hasSubscribers(self, topic):
        return topic in self.subs.keys() and len(self.subs[topic]) > 0

    def getSubscribers(self, topic):
        return self.subs[topic]

    def add(self, id, topic):
        print("subs:", self.subs)
        if topic not in self.subs.keys():
            self.subs[topic] = [id]
        else:
            # already subscribed
            if id in self.subs[topic]:
                return b'ASUB'
            else:
                self.subs[topic].append(id)
        return b'ACK'

    def remove(self, id, topic):
        if topic in self.subs.keys() and id in self.subs[topic]:
            self.subs[topic].remove(id)
            if len(self.subs[topic]) == 0:
                del self.subs[topic]
            return b'ACK'
        else:
            # already unsubbed
            return b'NSUB'


class PubSubInfo:
    def __init__(self):
        self.subs = Subscriptions()
        self.queues = MessageQueues()
        self.msg_pool = MessagePool()


class PubSubInstance:

    def __init__(self, pub_sub_info, reply):
        self.model = pub_sub_info
        self.reply = reply

    async def loop(self):
        await self.reply.poll()
        loop = asyncio.get_event_loop()
        loop.create_task(self.loop())
        await loop.create_task(self.handle_request())

    async def send(self, id, message):
        try:
            await self.reply.send_multipart([id, b"", message])
        except ZMQError as e:
            print(f"ZMQError: send failed - {str(e)}")

    async def handle_put(self, id, topic, message):
        if not self.model.subs.hasSubscribers(topic):
            await self.send(id, b'ACK')
        # subbed
        message_id = self.model.msg_pool.add(message)
        for subscriber in self.model.subs.getSubscribers(topic):
            self.model.queues.add(subscriber, topic, message_id)

        await self.send(id, b'ACK')

    async def handle_get(self, id, topic):
        # nothing in queue
        result = self.model.queues.peek(id, topic)
        if result is None:
            await self.send(id, b'N/A')
            return

        message = self.model.msg_pool.get(result)

        try:
            await self.reply.send_multipart([id, b"", message])
        except ZMQError as e:
            print(f"ZMQError: send failed - {str(e)}")
            return

        self.model.queues.pop(id, topic)
        self.model.msg_pool.cleanup(id, topic, self.model.queues)

    async def handle_sub(self, id, topic):
        await self.send(id, self.model.subs.add(id, topic))

    async def handle_unsub(self, id, topic):
        await self.send(id, self.model.subs.remove(id, topic))
        discarded_messages = self.model.queues.get_all(id, topic)
        if discarded_messages is None:
            return
        # remove related messages from queue and pool
        self.model.queues.remove(id, topic)
        for message_id in discarded_messages:
            self.model.msg_pool.cleanup(
                message_id, topic, self.model.queues)

    async def handle_request(self):
        messages = await self.reply.recv_multipart()
        for message in messages:
            print(message)
        id = messages[0]
        request = messages[2]
        if request == b'avail':
            await self.send(id, b'YES')
        topic = messages[3]
        if request == b'put':
            message = messages[4]
            await self.handle_put(id, topic, message)
        elif request == b'sub':
            await self.handle_sub(id, topic)
        elif request == b'unsub':
            await self.handle_unsub(id, topic)
        elif request == b'get':
            await self.handle_get(id, topic)

        else:
            print('Unexpected request: ' + request)
