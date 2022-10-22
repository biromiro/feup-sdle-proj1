import zmq

class Request:
    def __init__(self, socket, id):
        self.socket = socket
        self.id = id
    def send(self):
        pass
    def get_ack(self):
        if self.socket.poll(timeout=3000) != 0:
            response = self.socket.recv()
            print(response)

class Put(Request):
    def __init__(self, socket, topic, message):
        self.socket = socket
        self.topic = topic
        self.message = message
    def send(self):
        self.socket.send_multipart(b"put", self.topic, self.message)
        self.get_ack()

class Subscription(Request):
    def __init__(self, socket, id, topic, sub):
        super().__init__(socket, id)
        self.topic = topic
        self.sub = sub
    def send(self):
        if self.sub:
            subscription = b"sub" if self.sub else b"unsub"
            self.socket.send_multipart([subscription, self.id, self.topic])
        self.get_ack()

class Get(Request):
    def __init__(self, socket, id, topic):
        super().__init__(socket, id)
        self.topic = topic
    def send(self):
        self.socket.send_multipart(b"get", self.id, self.topic)
        self.get_ack()

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    with socket.connect("tcp://localhost:5563") as req:
        request = Subscription(req, b"13", b"bruh", True)
        request.send()

main()
