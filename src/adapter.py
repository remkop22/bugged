import asyncio
from typing import Tuple, Optional, Any
from clients import Client
from sockets import MessagingSocketClient

class CantHandle(Exception):

    def __init__(self, *args: object):
        super().__init__(*args)

class MessageHandler:

    def __init__(self):
        self._request_handlers = []
        self._response_handlers = []
        self._event_handlers = []
        self._message_handlers = []
        self.adapter: Optional[Any] = None

    def handle(self, headers, message):
        handlers = None
        if message['type'] == 'request':
            handlers = self._request_handlers
        elif message['type'] == 'response':
            handlers = self._response_handlers
        elif message['type'] == 'event':
            handlers = self._event_handlers
        else:
            if 'type' in message:
                raise Exception(f'unkown message type "{message["type"]}"')
            else:
                raise Exception(f'unkown message: "{message}"')

        for conditional, handler in handlers:
            if conditional(message):
                try:
                    handler(self.adapter, message)
                    return
                except CantHandle:
                    pass
        for handler in self._message_handlers:
            try:
                handler(self.adapter, message)
                return
            except CantHandle:
                pass
        print(f'warning message was not handled: {message}')

    def request(self, command:str = None):
        def decorator(func):
            self._request_handlers.append((lambda x: command is None or x["command"] == command, func))
            return func
        return decorator

    def event(self, event:str = None):
        def decorator(func):
            self._event_handlers.append((lambda x: event is None or  x["event"] == event, func))
            return func
        return decorator

    def response(self, command:str = None, succes:bool = None):
        lbda = lambda x: (command is None or  x["command"] == command) and (succes is None or succes == x["succes"])
        def decorator(func):
            self._response_handlers.append((lbda, func))
            return func
        return decorator

    def __call__(self, func):
        self._message_handlers.append(func)
        return func

class AdapterBase:

    message_handler = MessageHandler()

    def __init__(self, address: Tuple[str, int], adapterID, client:Client):
        self.client = client
        self.adapterID = adapterID
        self.socket_client = MessagingSocketClient(address, self.message_handler.handle)
        self.message_handler.adapter = self
        self.debug_client = None

    def connect(self):
        asyncio.run(self.socket_client.start())
        self.initialize()

    def _initialize(self):
        self.initialize()

    def initialize(self):
        pass

