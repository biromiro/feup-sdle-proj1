import zmq

SUBS = {}
QUEUES = {}

def queue_add(id, topic, message):
    # add new subscriber queue
    if id not in QUEUES.keys():
        QUEUES[id] = {topic : [message]}
        return
    # add new topic queue
    if topic not in QUEUES[id].keys():
        QUEUES[id][topic] = [message]
        return
    # add to existent queue
    QUEUES[id][topic].append(message)

def queue_remove(id, topic):
    # nothing to remove
    if id not in QUEUES.keys() or topic not in QUEUES[id].keys():
        return
    del QUEUES[id][topic]

def queue_pop(id, topic):
    # nothing to pop
    if id not in QUEUES.keys() or topic not in QUEUES[id].keys() or len(QUEUES[id][topic]) == 0:
        return
    return QUEUES[id][topic].pop(0)

def handle_put(reply, topic, message):
    # not subbed
    if topic not in SUBS.keys():
        reply.send(b'ACK')
        return
    # subbed
    for subscriber in SUBS[topic]:
        queue_add(subscriber, topic, message)
    reply.send(b'ACK')

def handle_get(reply, id, topic):
    result = queue_pop(id, topic)
    if result is None:
        reply.send(b'N/A')
    else:
        reply.send(result)

def handle_sub(reply, id, topic):
    # new topic
    if topic not in SUBS.keys():
        SUBS[topic] = [id]
    else:
        # already subscribed
        if id in SUBS[topic]:
            reply.send(b'ASUB')
            return
        else:
            SUBS[topic].append(id)
    # new subscriber
    if id not in QUEUES.keys():
        QUEUES[id] = []
    reply.send(b'ACK')

def handle_unsub(reply, id, topic):
    # already unsubbed
    if topic not in SUBS.keys() or id not in SUBS[topic]:
        reply.send(b'NSUB')
        return
    # unsub
    SUBS[topic].remove(id)
    if len(SUBS[topic]) == 0:
        del SUBS[topic]
    # remove related messages from queue
    queue_remove(id, topic)
    reply.send(b'ACK')

def handle_request(reply):
    messages = reply.recv_multipart()
    for message in messages:
        print(message)
    
    if messages[2] == b'put':
        topic = messages[3]
        message = messages[4]
        handle_put(reply, topic, message)
    elif messages[2] == b'sub':
        id = messages[3]
        topic = messages[4]
        handle_sub(reply, id, topic)
    elif messages[2] == b'unsub':
        id = messages[3]
        topic = messages[4]
        handle_unsub(reply, id, topic)
    elif messages[2] == b'get':
        id = messages[3]
        topic = messages[4]
        handle_get(reply, id, topic)
    else:
        print('unexpected message...')

def main():
    context = zmq.Context()
    reply = context.socket(zmq.ROUTER)
    #reply.setsockopt(zmq.ROUTER_MANDATORY, 1)
    reply.bind('tcp://127.0.0.1:5563')
    while True:
        reply.poll()
        handle_request(reply)

main()