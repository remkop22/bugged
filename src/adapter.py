import asyncio
from typing import Tuple, Optional, Any
from clients import Client
from sockets import MessagingSocketClient

class CantHandle(Exception):

    def __init__(self, *args: object):
        super().__init__(*args)

class MessageHandler:

    def __init__(self, instance):

        self._request_handlers = []
        self._response_handlers = []
        self._event_handlers = []
        self.instance = instance

        for prop in dir(instance):
            if hasattr(getattr(instance, prop), 'type'):
                func = getattr(instance, prop)
                if func.type == 'request':
                    lb = lambda x: func.command is None or func.command == x['command']
                    self._request_handlers.append((lb, func))
                elif func.type == 'event':
                    lb = lambda x: func.event is None or func.evnet == x['event']
                    self._event_handlers.append((lb, func))
                elif func.type == 'response':
                    lb = lambda x: (func.command is None or func.command == x['command']) \
                        and (func.success is None or func.success == x['success'])
                    self._response_handlers.append((lb, func))

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
                    handler(message)
                    return
                except CantHandle:
                    pass
        print(f'warning message was not handled: {message}')

    @staticmethod
    def request(command:str = None):
        def decorator(func):
            def wrapper(self, message, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'request'
            wrapper.command = command
            return wrapper
        return decorator

    @staticmethod
    def event(event:str = None):
        def decorator(func):
            def wrapper(self, message, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'event'
            wrapper.event = event
            return wrapper
        return decorator

    @staticmethod
    def response(command:str = None, success:bool = None):
        def decorator(func):
            def wrapper(self, message, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'response'
            wrapper.command = command
            wrapper.success = success
            return wrapper
        return decorator

class AdapterBase:

    def __init__(self, address: Tuple[str, int], adapterID, client:Client):
        self.client = client
        self.adapterID = adapterID
        self.socket_client = MessagingSocketClient(address, self._handle_message)
        self.debug_client = None
        self.message_handler = MessageHandler(self)

    def connect(self):
        asyncio.run(self.socket_client.start())

    def _handle_message(self, message, header):
        self.message_handler.handle(message, header)
        self.handle_message(message)

    def handle_message(self, message):
        pass


