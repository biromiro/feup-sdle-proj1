import zmq
import aiofiles
import asyncio
import pickle5 as pickle
import sys
import os.path
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
    if (os.path.isfile(STATE_FILE_NAME)):
        with open(STATE_FILE_NAME, mode='rb') as infile:
            obj = pickle.load(infile)
    return obj

async def save_state_to_file(pub_sub):
    print('Hello1')
    while True:
        async with aiofiles.open(STATE_FILE_NAME, 'wb') as outfile:
            print('writing to file')
            pickle.dump(pub_sub, outfile)
            print('wrote to file')
        print('will await for 5 secs')
        await asyncio.sleep(5)
        print('awaited')
    
async def pub_sub_loop(pub_sub):
    print('hello')
    pub_sub.loop()

async def main():
    context = zmq.Context()
    reply = context.socket(zmq.REP)
    #reply.setsockopt(zmq.ROUTER_MANDATORY, 1)
    reply.bind('tcp://127.0.0.1:5563')
    
    pub_sub_info = get_state()
    if pub_sub_info is None:
        pub_sub = PubSubInfo()
    
    pub_sub = PubSubInstance(pub_sub, reply)
    
    await asyncio.gather(
        save_state_to_file(pub_sub_info),
        pub_sub_loop(pub_sub)
    )
    

if __name__ == '__main__':
    asyncio.run(main())