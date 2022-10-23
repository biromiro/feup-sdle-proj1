import pickle
import aiofiles
import os
from pubsub import PubSubInfo, PubSubInstance

STATE_FILE_NAME = './server_files/state'
EXTENSION = '.pickle'


def get_state(port):
    obj = None
    if os.path.isfile(f"{STATE_FILE_NAME}{port}{EXTENSION}"):
        with open(f"{STATE_FILE_NAME}{port}{EXTENSION}", mode='rb') as infile:
            obj = pickle.load(infile)
            print(obj)
    return obj


async def save_state_to_file(pub_sub, port):
    async with aiofiles.open(f"{STATE_FILE_NAME}{port}{EXTENSION}", 'wb') as outfile:
        print(f"Saving state...")
        val = pickle.dumps(pub_sub)
        await outfile.write(val)
