
from bugged.dap.messages import Event, Message, ProtocolMessage, Request, Response


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
                    lb = lambda m, f: f.command is None or f.command == m.command
                    self._request_handlers.append((lb, func_match))
                elif func_match.type == 'event':
                    lb = lambda m, f: f.event is None or f.event == m.event
                    self._event_handlers.append((lb, func_match))
                elif func_match.type == 'response':
                    lb = lambda m, f: (f.command is None or f.command == m.command) \
                        and (f.success is None or f.success == m.success)
                    self._response_handlers.append((lb, func_match))

    def handle(self, message: ProtocolMessage):
        handlers = None
        if isinstance(message, Request):
            handlers = self._request_handlers
        elif isinstance(message, Response):
            handlers = self._response_handlers
        elif isinstance(message, Event):
            handlers = self._event_handlers
        else:
            raise Exception('unkown message')

        handled = False
        for index, (conditional, handler) in enumerate(reversed(handlers)):
            if conditional(message, handler):
                try:
                    handler(message)
                    handled = True
                    if hasattr(handler, 'persist') and not handler.persist:
                        handlers.pop(index)
                        print('popped')
                    if not handler.propogate:
                        return
                except CantHandle:
                    pass
        if not handled:
            print(f'warning message was not handled: {message}')

    @staticmethod
    def request(command:str = None, propogate=False):
        def decorator(func):
            def wrapper(message: Request, *args, **kwargs):
                func(message, *args, **kwargs)
            wrapper.type = 'request'
            wrapper.command = command
            wrapper.propogate = propogate
            return wrapper
        return decorator

    @staticmethod
    def event(event:str = None, propogate=False):
        def decorator(func):
            def wrapper(self, message: Event, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'event'
            wrapper.event = event
            wrapper.propogate = propogate
            return wrapper
        return decorator


    @staticmethod
    def response(command:str = None, success:bool = None, propogate=False):
        def decorator(func):
            def wrapper(self, message: Response, *args, **kwargs):
                func(self, message, *args, **kwargs)
            wrapper.type = 'response'
            wrapper.command = command
            wrapper.success = success
            wrapper.propogate = propogate
            return wrapper
        return decorator

    def register_callback(self, request: Request, success_callback, error_callback, propogate):
        if success_callback or error_callback:
            def wrapper(message: Response, *args, **kwargs):
                if (error_callback is None or message.success) and success_callback:
                    success_callback(message, *args, **kwargs)
                elif not message.success:
                    error_callback(message, *args, **kwargs)

            wrapper.type = 'response'
            wrapper.command = None
            wrapper.success = None
            wrapper.propogate = propogate
            wrapper.seq = request.seq
            wrapper.persist = False

            self._response_handlers.append((lambda m, f: f.seq == m.request_seq, wrapper))


