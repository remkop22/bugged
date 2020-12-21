import asyncio
from threading import Thread
from typing import Tuple
from bugged.dap.messages import Message, ProtocolMessage, Request
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
        self.thread = Thread(target=self._connect)
        self.thread.start()
        self.socket_client.connected.wait()

    def _connect(self):
        asyncio.run(self.socket_client.start())

    def _handle_message(self, message_dict):
        message = ProtocolMessage.from_dict(message_dict)
        self.message_handler.handle(message)
        self.handle_message(message)

    def handle_message(self, message: ProtocolMessage):
        pass

    def send(self, message: ProtocolMessage, success_callback=None, error_callback=None, propogate=False):
        if isinstance(message, Request) and (success_callback or error_callback):
            self.message_handler.register_callback(message, success_callback, error_callback, propogate)
        elif (success_callback or error_callback) and not isinstance(message, Request):
            raise Exception('cannot register callback on event or response')
        self.socket_client.send(message)

