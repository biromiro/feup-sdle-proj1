import zmq

pair_addr = 'tcp://127.0.0.1:5565'

class BinaryStar:
    def __init__(self, service, pair, role):
        self.role = role
        self.service = service
        self.pair = pair
        # establish connection
        if self.role == 'active':
            pair.bind(pair_addr)
        elif self.role == 'passive':
            pair.connect(pair_addr)
    
    def run(self):
        # parallel tasks:
        # - if active:
        #   - service.loop()
        #   - pair.send_state()
        # - if passive:
        #   - pair.receive_state()
        #     - on timeout: assume active
        pass