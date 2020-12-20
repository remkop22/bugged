from bugged.base import AdapterBase, MessageHandler
from bugged.base import ClientBase, Process

from typing import Tuple
from bugged.dap.messages import InitializeRequest, Request, Response
from bugged.dap.types import Scope, StackFrame, Thread

class BuggedAdapter(AdapterBase):

    def __init__(self, address: Tuple[str, int],  client: ClientBase):
        super().__init__(address, 'bugged', client)
        self.initialized = False
        self.configured = False
        self.start_mode = self.attach
        self.request_all_scopes = True

    def initialize(self):
        def handle_init(message):
            #print(Response(**message).__dict__)
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

    def request_threads(self):
        def thread_handler(msg):
            self.client.process.threads = [Thread(**thread) for thread in msg['body']['threads']]
            self.client.update_threads()
            self.request_stracktrace(self.client.focussed_thread_id)

        self.send(Request('threads'), thread_handler, self.raise_message)

    def request_stracktrace(self, thread_id):
        def stack_handler(msg):
            stackframes = [StackFrame(**stack) for stack in msg['body']['stackFrames']]
            self.client.process.get_thread(thread_id).stackframes = stackframes
            self.client.focussed_frame_id = stackframes[0].id
            self.client.update_stacks()
            self.request_scopes(self.client.focussed_frame_id)

        self.send(Request('stackTrace', {"threadId": thread_id}), stack_handler, self.raise_message)

    def request_scopes(self, frame_id):
        def scope_handler(msg):
            scopes = [Scope(**scope) for scope in msg['body']['scopes']]
            self.client.process.get_stackframe(frame_id).scopes = scopes
            self.client.update_scopes()
            for scope in scopes:
                self.request_variables(scope.variablesReference)
        self.send(Request('scopes', {'frameId': frame_id}), scope_handler, self.raise_message)

    def request_variables(self, variables_reference:int):
        def variable_handler(msg):
            self.client.update_variables()

        self.send(Request('variables', arguments={"variablesReference": variables_reference}), variable_handler, self.raise_message)

    @MessageHandler.request(propogate=True)
    def handle_request(self, message):
        print(message)

    @MessageHandler.response(propogate=True)
    def handle_response(self, message):
        pass
        #print(message)

    @MessageHandler.event(propogate=True)
    def handle_event(self, message):
        pass
        # print(message)

    @MessageHandler.event('initialized')
    def handle_init_event(self, message):
        self.initialized = True
        self.configure()

    @MessageHandler.event('stopped')
    def handle_stop(self, message):
        print("debugger stopped")
        self.client.focussed_thread_id =  message['body']['threadId']
        self.request_threads()

    @MessageHandler.event('process')
    def handle_process(self, message):
        process = Process(**message['body'])
        self.client.process = process

    @MessageHandler.event('thread')
    def handle_thread(self, message):
        # for now only update on stopped
        pass

    def raise_message(self, message):
        raise Exception(message['message'])

if __name__ == '__main__':
    client = ClientBase('vim-bugger', 'vim-bugged', 'en-US')
    adapter = BuggedAdapter(('localhost', 5678), client)
    adapter.start()
    adapter.initialize()
