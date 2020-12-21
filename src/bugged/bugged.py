from bugged.base import AdapterBase, MessageHandler
from bugged.base import ClientBase, Process

from typing import Tuple
from bugged.dap.messages import InitializeRequest, Request, Response
from bugged.dap.types import Scope, StackFrame, Thread

class DebugAdapterException(Exception):

    pass

class BuggedAdapter(AdapterBase):

    def __init__(self, address: Tuple[str, int],  client: ClientBase):
        super().__init__(address, 'bugged', client)
        self.initialized = False
        self.configured = False
        self.stopped = False

    def initialize(self):
        def handle_init(message):
            #print(Response(**message).__dict__)
            #TODO handle cababilities defined in this response
            self.client.initialized()

        self.send(InitializeRequest(self), handle_init, self.raise_message)

    def attach(self):
        self.send(Request('attach', {"test": ""}), self.client.started, self.raise_message)

    def launch(self):
        self.send(Request('launch'), self.client.started, self.raise_message)

    def send_configuration(self):
        #TODO: send breakpoints to debugger
        self.send(Request('configurationDone'), error_callback=self.raise_message)

    def continue_debug(self):
        def handle_continue(msg):
            self.stopped = False
            self.client.continued()
        self.send(Request('continue'), handle_continue, self.raise_message)

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


    def send_breakpoints(self):
        pass

    @MessageHandler.request(propogate=True)
    def handle_request(self, message):
        print(message)

    @MessageHandler.response(propogate=True)
    def handle_response(self, message):
        pass

    @MessageHandler.event(propogate=True)
    def handle_event(self, message):
        pass

    @MessageHandler.event('initialized')
    def handle_init_event(self, message):
        self.initialized = True
        self.client.configure()
        self.send_configuration()

    @MessageHandler.event('stopped')
    def handle_stop(self, message):
        print("debugger stopped")
        self.client.stopped = False
        self.client.focussed_thread_id =  message['body']['threadId']
        self.request_threads()
        self.client.stopped()

    @MessageHandler.event('process')
    def handle_process(self, message):
        process = Process(**message['body'])
        self.client.process = process

    @MessageHandler.event('thread')
    def handle_thread(self, message):
        # for now only update on stopped
        pass

    def raise_message(self, message):
        raise DebugAdapterException(message['message'])
