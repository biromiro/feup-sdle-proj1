import zmq
import zmq.asyncio
import aiofiles
import asyncio
import pickle
import sys
import os.path
import threading
from pubsub import PubSubInfo, PubSubInstance

# topic -> subscriber
#subs = {}
# subscriber -> topic -> [message_id]
#queues = {}
# message_id -> message
#msg_pools = {}
#msg_id = 0

STATE_FILE_NAME = './server_files/state.pickle'


def get_state():
    obj = None
    if os.path.isfile(STATE_FILE_NAME):
        with open(STATE_FILE_NAME, mode='rb') as infile:
            obj = pickle.load(infile)
            print(obj)
    return obj


async def save_state_to_file(pub_sub):
    while True:
        async with aiofiles.open(STATE_FILE_NAME, 'wb') as outfile:
            print(f"Saving state...")
            val = pickle.dumps(pub_sub)
            await outfile.write(val)
        await asyncio.sleep(2)


async def pub_sub_loop(pub_sub):
    await pub_sub.loop()


async def main():
    context = zmq.asyncio.Context()
    reply = context.socket(zmq.ROUTER)
    reply.setsockopt(zmq.ROUTER_MANDATORY, 1)
    reply.bind('tcp://127.0.0.1:5563')

    pub_sub_info = get_state()
    if pub_sub_info is None:
        pub_sub_info = PubSubInfo()

    pub_sub = PubSubInstance(pub_sub_info, reply)

    task_1 = asyncio.create_task(save_state_to_file(pub_sub_info))
    task_2 = asyncio.create_task(pub_sub_loop(pub_sub))

    await asyncio.gather(
        task_1,
        task_2
    )


if __name__ == '__main__':

    if sys.platform:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
