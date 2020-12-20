from threading import Thread
from adapter import AdapterBase, MessageHandler
from clients import Client
from typing import Tuple
from dap import InitializeRequest
import time

class BuggedAdapter(AdapterBase):

    def __init__(self, address: Tuple[str, int],  client: Client):
        super().__init__(address, 'bugged', client)

    def initialize(self):
        print('initialized')

    def handle_message(self, message):
        pass

    @MessageHandler.event()
    def handle_event(self, message):
        print(message)

client = Client('vim-bugger', 'vim-bugged', 'en-US')
adapter = BuggedAdapter(('localhost', 5678), client)
thread = Thread(target=adapter.connect)
thread.start()

thread.join()
