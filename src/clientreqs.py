import zmq


class Request:
    def __init__(self, args, socket):
        socket.setsockopt(zmq.IDENTITY, args.id)
        socket.connect('tcp://127.0.0.1:5563')
        self.socket = socket

    def send(self):
        pass

    def get_ack(self):
        if self.socket.poll(timeout=3000) != 0:
            response = self.socket.recv()
            print(response)


class Put(Request):
    def __init__(self, args, socket):
        socket.connect('tcp://127.0.0.1:5563')
        self.socket = socket
        self.topic = args.topic
        self.message = args.text

    def send(self):
        self.socket.send_multipart([b'put', self.topic, self.message])
        self.get_ack()


class Subscribe(Request):
    def __init__(self, args, socket):
        super().__init__(args, socket)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'sub', self.topic])
        self.get_ack()


class Unsubscribe(Request):
    def __init__(self, args, socket):
        super().__init__(args, socket)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'unsub', self.topic])
        self.get_ack()


class Get(Request):
    def __init__(self, args, socket):
        super().__init__(args, socket)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'get', self.topic])
        self.get_ack()
