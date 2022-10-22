import zmq
import argparse


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


def get(args):
    print(f"The arguments are: id={args.id}, topic={args.topic}")


def put(args):
    if (args.file):
        print(
            f"The arguments are: topic={args.topic}, message={args.file.read()}")
    else:
        print(
            f"The arguments are: topic={args.topic}, message={args.text}")


def subscribe(args):
    print(f"The arguments are: id={args.id}, topic={args.topic}")
    return


def unsubscribe(args):
    print(f"The arguments are: id={args.id}, topic={args.topic}")
    return


FUNCTION_MAP = {'get': get,
                'put': put,
                'subscribe': subscribe,
                'unsubscribe': unsubscribe}


def arg_parse():
    parser = argparse.ArgumentParser(
        description='Select one of the possible commands: get, put, subscribe, unsubscribe')

    # this serves as a parent parser
    base_parser = argparse.ArgumentParser(add_help=False)

    # add common args

    get = argparse.ArgumentParser(add_help=False)
    get.add_argument('id', help='number', type=int)
    get.add_argument('topic', help='string', type=str)

    put = argparse.ArgumentParser(add_help=False)
    put_group = put.add_mutually_exclusive_group(required=True)
    put_group.add_argument('-t', '--text', help='Text')
    put_group.add_argument('-f', '--file', type=argparse.FileType('r'),
                           help='File containing the text')
    put.add_argument('topic', help='string', type=str)

    subscribe = argparse.ArgumentParser(add_help=False)
    subscribe.add_argument('id', help='number', type=int)
    subscribe.add_argument('topic', help='string', type=str)

    unsubscribe = argparse.ArgumentParser(add_help=False)
    unsubscribe.add_argument('id', help='number', type=int)
    unsubscribe.add_argument('topic', help='string', type=str)

    # subparsers
    subparsers = parser.add_subparsers(title="commands", dest="command")
    subparsers.required = True
    subparsers.add_parser('get', help='get',
                          parents=[base_parser, get])

    subparsers.add_parser('put', help='put',
                          parents=[base_parser, put])

    subparsers.add_parser('subscribe', help='subscribe',
                          parents=[base_parser, subscribe])

    subparsers.add_parser('unsubscribe', help='unsubscribe',
                          parents=[base_parser, unsubscribe])

    return parser.parse_args()


def main():
    args = arg_parse()
    func = FUNCTION_MAP[args.command]
    func(args)
    #context = zmq.Context()
    #socket = context.socket(zmq.REQ)
    # with socket.connect("tcp://localhost:5563") as req:
    #    request = Subscription(req, b"13", b"bruh", True)
    #    request.send()


main()
