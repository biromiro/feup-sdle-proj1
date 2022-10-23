import zmq


class Request:
    def __init__(self, args, socket, server):
        socket.setsockopt(zmq.IDENTITY, args.id)
        socket.connect(server)
        self.socket = socket

    def send(self):
        pass

    def get_ack(self):
        if self.socket.poll(timeout=10000) != 0:
            response = self.socket.recv()
            return response


class Put(Request):
    def __init__(self, args, socket, server):
        socket.connect(server)
        self.socket = socket
        self.topic = args.topic
        self.message = args.text

    def send(self):
        self.socket.send_multipart([b'put', self.topic, self.message])


class Subscribe(Request):
    def __init__(self, args, socket, server):
        super().__init__(args, socket, server)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'sub', self.topic])


class Unsubscribe(Request):
    def __init__(self, args, socket, server):
        super().__init__(args, socket, server)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'unsub', self.topic])


class Get(Request):
    def __init__(self, args, socket, server):
        super().__init__(args, socket, server)
        self.topic = args.topic

    def send(self):
        self.socket.send_multipart([b'get', self.topic])
