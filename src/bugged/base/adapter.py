import asyncio
from threading import Thread
from typing import Tuple
from bugged.messaging import MessagingSocketClient, MessageHandler

class AdapterBase:

    def __init__(self, address: Tuple[str, int], adapterID, client:'Client'):
        self.client = client
        self.client.adapter = self
        self.adapterID = adapterID
        self.socket_client = MessagingSocketClient(address, self._handle_message)
        self.debug_client = None
        self.message_handler = MessageHandler(self)
        self.thread = None

    def start(self):
        self.thread = Thread(target=self.connect)
        self.thread.start()
        self.socket_client.connected.wait()

    def connect(self):
        asyncio.run(self.socket_client.start())

    def _handle_message(self, message, header):
        self.message_handler.handle(message, header)
        self.handle_message(message)

    def handle_message(self, message):
        pass

    def send(self, message, success_callback=None, error_callback=None, propogate=False):
        self.message_handler.register_callback(message, success_callback, error_callback, propogate)
        self.socket_client.send(message)

