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
            return
        return self.queues[sub][topic].pop(0)

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
        self.pub_sub = pub_sub_info
        self.reply = reply

    def loop(self):
        while True:
            self.reply.poll()
            self.handle_request()

    def handle_put(self, topic, message):
        if not self.pub_sub.subs.hasSubscribers(topic):
            self.reply.send(b'ACK')
            return
        # subbed
        message_id = self.pub_sub.msg_pool.add(message)
        for subscriber in self.pub_sub.subs.getSubscribers(topic):
            self.pub_sub.queues.add(subscriber, topic, message_id)
        self.reply.send(b'ACK')

    def handle_get(self, id, topic):
        # nothing in queue
        result = self.pub_sub.queues.pop(id, topic)
        if result is None:
            self.reply.send(b'N/A')
            return

        message = self.pub_sub.msg_pool.get(result)

        self.pub_sub.msg_pool.cleanup(id, topic, self.pub_sub.queues)
        self.reply.send(message)

    def handle_sub(self, id, topic):
        self.reply.send(self.pub_sub.subs.add(id, topic))

    def handle_unsub(self, id, topic):
        self.reply.send(self.pub_sub.subs.remove(id, topic))
        discarded_messages = self.pub_sub.queues.get_all(id, topic)
        if discarded_messages is None:
            return
        # remove related messages from queue and pool
        self.pub_sub.queues.remove(id, topic)
        for message_id in discarded_messages:
            self.pub_sub.msg_pool.cleanup(
                message_id, topic, self.pub_sub.queues)

    def handle_request(self):
        messages = self.reply.recv_multipart()
        for message in messages:
            print(message)

        if messages[0] == b'put':
            topic = messages[1]
            message = messages[2]
            self.handle_put(topic, message)
        elif messages[0] == b'sub':
            id = messages[1]
            topic = messages[2]
            self.handle_sub(id, topic)
        elif messages[0] == b'unsub':
            id = messages[1]
            topic = messages[2]
            self.handle_unsub(id, topic)
        elif messages[0] == b'get':
            id = messages[1]
            topic = messages[2]
            self.handle_get(id, topic)
        elif messages[0] == b'avail':
            self.reply.send(b'YES')
        else:
            print('unexpected message!!')
