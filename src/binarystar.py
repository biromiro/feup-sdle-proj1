import zmq
import asyncio
import pickle
from aux_func import save_state_to_file

PAIR_ADDR = 'tcp://127.0.0.1:5565'


class BinaryStar:
    def __init__(self, service, pair, role, port):
        self.role = role
        self.service = service
        self.pair = pair
        self.service_active = False
        self.port = port
        # establish connection
        self.setup_pair_socket()

    def setup_pair_socket(self):
        if self.role == 'active':
            try:
                self.pair.bind(PAIR_ADDR)
            except zmq.error.ZMQError:
                print('Failed to bind to pair socket, is there another active instance?')
                raise
        elif self.role == 'passive':
            try:
                self.pair.connect(PAIR_ADDR)
            except zmq.error.ZMQError:
                print('Failed to connect to pair socket, is there an active instance?')
                raise

    async def save_file_loop(self):
        await save_state_to_file(self.service.model, self.port)
        await asyncio.sleep(5)
        loop = asyncio.get_event_loop()
        loop.create_task(self.save_file_loop())

    async def run(self):
        # parallel tasks:
        loop = asyncio.get_event_loop()
        if self.role == 'active':
            if not self.service_active:
                loop.create_task(self.service.loop())
                loop.create_task(self.save_file_loop())
            val = pickle.dumps(self.service.model)
            await self.pair.send(val)
            await asyncio.sleep(5)
        if self.role == 'passive':
            res = await self.pair.poll(timeout=15000)
            if res == 0:
                self.role = 'active'
                self.pair.disconnect(PAIR_ADDR)
                self.setup_pair_socket()

                print('Active instance has failed, taking over')
            else:
                response = await self.pair.recv()
                model = pickle.loads(response)
                self.service.model = model
                loop.create_task(save_state_to_file(
                    self.service.model, self.port))
        await loop.create_task(self.run())
