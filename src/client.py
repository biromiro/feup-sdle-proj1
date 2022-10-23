import zmq
import argparse
from clientreqs import Subscribe, Unsubscribe, Get, Put

REQUEST_DICT = {
    'subscribe': Subscribe,
    'unsubscribe': Unsubscribe,
    'get': Get,
    'put': Put
}


def arg_parse():
    parser = argparse.ArgumentParser(
        description='Select one of the possible commands: get, put, subscribe, unsubscribe')

    # this serves as a parent parser
    base_parser = argparse.ArgumentParser(add_help=False)

    # add common args

    get = argparse.ArgumentParser(add_help=False)
    get.add_argument('id', help='string', type=str)
    get.add_argument('topic', help='string', type=str)

    put = argparse.ArgumentParser(add_help=False)
    put_group = put.add_mutually_exclusive_group(required=True)
    put_group.add_argument('-t', '--text', help='Text')
    put_group.add_argument('-f', '--file', type=argparse.FileType('r'),
                           help='File containing the text')
    put.add_argument('topic', help='string', type=str)

    subscribe = argparse.ArgumentParser(add_help=False)
    subscribe.add_argument('id', help='string', type=str)
    subscribe.add_argument('topic', help='string', type=str)

    unsubscribe = argparse.ArgumentParser(add_help=False)
    unsubscribe.add_argument('id', help='string', type=str)
    unsubscribe.add_argument('topic', help='string', type=str)

    # subparsers
    subparsers = parser.add_subparsers(title='commands', dest='command')
    subparsers.required = True
    subparsers.add_parser('get', help='get',
                          parents=[base_parser, get])

    subparsers.add_parser('put', help='put',
                          parents=[base_parser, put])

    subparsers.add_parser('subscribe', help='subscribe',
                          parents=[base_parser, subscribe])

    subparsers.add_parser('unsubscribe', help='unsubscribe',
                          parents=[base_parser, unsubscribe])

    args = parser.parse_args()
    if args.command == 'put':
        args.text = args.file.read() if args.text is None else args.text
    for arg in vars(args):
        if arg != 'command' and arg != 'file':
            setattr(args, arg, bytes(getattr(args, arg), 'utf-8'))

    return args


def main():
    args = arg_parse()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    request = REQUEST_DICT[args.command](args, socket)
    request.send()


if __name__ == '__main__':
    main()
