import asyncio
from threading import Thread
from typing import Tuple
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
                func_match = getattr(instance, prop)
                if func_match.type == 'request':
                    lb = lambda m, f: f.command is None or f.command == m['command']
                    self._request_handlers.append((lb, func_match))
                elif func_match.type == 'event':
                    lb = lambda m, f: f.event is None or f.event == m['event']
                    self._event_handlers.append((lb, func_match))
                elif func_match.type == 'response':
                    lb = lambda m, f: (f.command is None or f.command == m['command']) \
                        and (f.success is None or f.success == m['success'])
                    self._response_handlers.append((lb, func_match))

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

        handled = False
        for index, (conditional, handler) in enumerate(reversed(handlers)):
            if conditional(message, handler):
                try:
                    handler(message)
                    handled = True
                    if not handler.propogate:
                        return
                    if hasattr(handler, 'persist') and not handler.persist:
                        handlers.pop(index)
                        print('popped')
                except CantHandle:
                    pass
        if not handled:
            print(f'warning message was not handled: {message}')

    @staticmethod
    def request(command:str = None, propogate=False):
        def decorator(func):
            def wrapper(message, *args, **kwargs):
                func(message, *args, **kwargs)
            wrapper.type = 'request'
            wrapper.command = command
            wrapper.propogate = propogate
            return wrapper
            return wrapper2
        return decorator

    @staticmethod
    def event(event:str = None, propogate=False):
        def decorator(func):
            def wrapper(self, message, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'event'
            wrapper.event = event
            wrapper.propogate = propogate
            return wrapper
        return decorator


    @staticmethod
    def response(command:str = None, success:bool = None, propogate=False):
        def decorator(func):
            def wrapper(self, message, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'response'
            wrapper.command = command
            wrapper.success = success
            wrapper.propogate = propogate
            return wrapper
        return decorator

class AdapterBase:

    def __init__(self, address: Tuple[str, int], adapterID, client:Client):
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
        if success_callback or error_callback:
            if message.type != 'request':
                raise Exception('event or response does not accept callbacks')

            def wrapper(message, *args, **kwargs):
                if (error_callback is None or message["success"]) and success_callback:
                    success_callback(message, *args, **kwargs)
                elif not message["success"]:
                    error_callback(message, *args, **kwargs)

            wrapper.type = 'response'
            wrapper.command = None
            wrapper.success = None
            wrapper.propogate = propogate
            wrapper.seq = message.seq
            wrapper.persist = False

            self.message_handler._response_handlers.append((lambda m, f: f.seq == m["request_seq"], wrapper))
        self.socket_client.send(message)



