import zmq
import zmq.asyncio
import asyncio
import sys
from pubsub import PubSubInfo, PubSubInstance
from binarystar import BinaryStar
import serverlist
from argparse import ArgumentParser
from aux_func import get_state
# topic -> subscriber
#subs = {}
# subscriber -> topic -> [message_id]
#queues = {}
# message_id -> message
#msg_pools = {}
#msg_id = 0


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('port', choices=[0, 1], type=int)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--active", action="store_true", default=False)
    group.add_argument("-p", "--passive", action="store_true", default=False)
    return parser.parse_args()


# async def pub_sub_loop(pub_sub):
#    await pub_sub.loop()


async def main(args):
    context = zmq.asyncio.Context()

    reply = context.socket(zmq.ROUTER)
    # monitor reply reception
    reply.setsockopt(zmq.ROUTER_MANDATORY, 1)
    # time out stray messages due to bstar
    reply.setsockopt(zmq.LINGER, 5000)
    # choose with args
    address = serverlist.SERVERS[args.port]
    try:
        reply.bind(address)
    except zmq.error.ZMQBaseError as e:
        print('Failed to bind to pair socket, is there another active instance?')
        return

    pub_sub_info = get_state(args.port)
    if pub_sub_info is None:
        pub_sub_info = PubSubInfo()

    pub_sub = PubSubInstance(pub_sub_info, reply)
    role = 'active' if args.active else 'passive'
    binary_star = BinaryStar(
        pub_sub, context.socket(zmq.PAIR), role, args.port)

    loop = asyncio.get_event_loop()

    await loop.create_task(binary_star.run())


if __name__ == '__main__':
    args = parse_args()

    if sys.platform.startswith('linux'):
        asyncio.set_event_loop_policy(None)
    else:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(args))
