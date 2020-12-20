from threading import Thread
from adapter import AdapterBase, MessageHandler
from clients import Client
from typing import Tuple
from dap import InitializeRequest, Request
import time

class BuggedAdapter(AdapterBase):

    def __init__(self, address: Tuple[str, int],  client: Client):
        super().__init__(address, 'bugged', client)
        self.initialized = False
        self.configured = False
        self.start_mode = self.attach

    def initialize(self):
        def handle_init(message):
            #TODO handle cababilities defined in this response
            self.start_mode()

        self.send(InitializeRequest(self), handle_init, self.raise_message)

    def attach(self):
        self.send(Request('attach', {"test": ""}), error_callback=self.raise_message)

    def launch(self):
        self.send(Request('launch'), error_callback=self.raise_message)

    def configure(self):
        # put configuration (breakpoints etc...) here
        # than call cofiguration done, or alternatively register it as a callback for last req
        self.send(Request('configurationDone'), lambda msg: print('started!'))

    def continue_debug(self):
        self.socket_client.send(Request('continue'))

    @MessageHandler.request(propogate=True)
    def handle_request(self, message):
        print(message)

    @MessageHandler.response(propogate=True)
    def handle_response(self, message):
        print(message)

    @MessageHandler.event(propogate=True)
    def handle_event(self, message):
        print(message)

    @MessageHandler.event('initialized')
    def handle_init_event(self, message):
        self.initialized = True
        self.configure()

    @MessageHandler.event('stopped')
    def handle_stop(self, message):
        self.continue_debug()

    def raise_message(self, message):
        raise Exception(message['message'])

client = Client('vim-bugger', 'vim-bugged', 'en-US')
adapter = BuggedAdapter(('localhost', 5678), client)
adapter.start()
adapter.initialize()
