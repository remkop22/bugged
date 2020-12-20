from typing import Literal, Any, Optional
import json
from bugged.utils import without

seq_count = 0

class Message:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def as_dict(self) -> dict:
        return {key: val for key, val in self.__dict__.items() if val is not None}

    @staticmethod
    def from_dict(msg) -> 'Message':
        if msg['type'] == 'request':
            return Request(**msg)
        elif msg['type'] == 'response':
            return Response(**msg)
        elif msg['type'] == 'event':
            return Event(**msg)
        else:
            raise Exception(f'unkown message type {msg["type"]}')

    @property
    def header(self):
        return f"Content-Length: {len(self.content)}\r\n\r\n"

    @property
    def content(self):
        return json.dumps(self.as_dict())


class ProtocolMessage(Message):

    def __init__(self, type: Literal['request', 'response', 'event'], **kwargs):
        super().__init__(**kwargs)
        global seq_count
        self.seq: int = seq_count
        seq_count += 1
        self.type = type

class Request(ProtocolMessage):

    def __init__(self, command: str, arguments: Optional[Any] = None, **kwargs):
        super().__init__('request', **without(kwargs, ['type']))
        self.arguments = arguments
        self.command = command

class Event(ProtocolMessage):

    def __init__(self, event:str, body: Optional[Any] = None, **kwargs):
        super().__init__('event', **without(kwargs, ['type']))
        self.event = event
        self.body = body

class Response(ProtocolMessage):

    def __init__(self, command: str,  message: Optional[str] = None, body: Optional[Any] = None, success: Optional[bool] = None, **kwargs):
        super().__init__('response', **without(kwargs, ['type']))
        self.success = success
        self.command = command
        self.message = message
        self.body = body

class InitializeRequest(Request):

    def __init__(self, adapter):
        super().__init__('initialize', {
            "adapterID" : adapter.adapterID,
            **adapter.client.configuration
        })
