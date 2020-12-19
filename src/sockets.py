from asyncio import open_connection, run
import asyncio
from typing import Tuple, List
from threading import Thread
import json

class MessagingSocketClient():

    def __init__(self, address: Tuple[str, int], message_handler):
        self.host, self.port = address
        self.message_handler = message_handler
        self.is_running = False
        self.is_reading = False

    async def start(self):
        await self.connect()
        self.is_running = True
        asyncio.create_task(self.run())

    async def run(self):
        while self.is_running:
            await self.read()

    async def connect(self):
        self.reader, self.writer = await open_connection(self.host, self.port)

    def send(self, message):
        encoded = message.header.encode('ascii') + message.content.encode('utf-8')
        self.writer.write(encoded)

    async def read(self):
        self.is_reading = True
        header_buffer = await self.reader.readuntil(b'\r\n\r\n')
        headers = [header for header in header_buffer.decode('ascii').strip().split('\r\n')]
        headers = {key:val for key, val in [header.split(':') for header in headers]}
        content_len = int(headers['Content-Length'])
        content = json.loads(await self.reader.read(content_len))

        self.is_reading = False
        self.message_handler(headers, content)
