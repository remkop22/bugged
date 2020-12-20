from typing import List, Literal, Optional
from adapter import AdapterBase
from dap.types import SourceBreakpoint, StackFrame, Thread, Variable

class Process:

    def __init__(self, name: str, systemProcessId: Optional[int] = None,
                 isLocalProcess: Optional[bool] = None,
                 startMethod: Optional[Literal['launch', 'attach', 'attachForSuspendedLaunch']] = None,
                 pointerSize: Optional[int] = None ):
        self.name = name
        self.process_id = systemProcessId
        self.is_local = isLocalProcess
        self.start_method = startMethod
        self.pointer_size = pointerSize

        self.threads:List[Thread] = []

    def get_thread(self, thread_id):
        for thread in self.threads:
            if thread.id == thread_id:
                return thread

    def get_stackframe(self, stackframe_id):
        for thread in self.threads:
            res = thread.get_stackframe(stackframe_id)
            if res:
                return res

class Client:

    def __init__(self, clientID: str, clientName: str, locale: str):

        self.configuration = {
            "clientID": clientID,
            "clientName": clientName,
            "locale": locale,
            "linesStartAt1": True,
            "columnsStartAt1": True,
            "pathFormat": 'path',
            "supportsVariableType": False,
            "supportsVariablePaging": False,
            "supportsRunInTerminalRequest": False,
            "supportsMemoryReferences": False,
            "supportsProgressReporting": False,
            "supportsInvalidatedEvent": False
        }

        self.breakpoints:List[SourceBreakpoint] = []
        self.process: Optional[Process] = None
        self.focussed_thread_id: Optional[int] = None
        self.focussed_frame_id: Optional[int] = None
        self.adapter: Optional[AdapterBase] = None

    @property
    def focussed_thread(self):
        if self.focussed_thread_id:
            return self.process.get_thread(self.focussed_thread_id)

    @property
    def focussed_stackframe(self):
        if self.focussed_frame_id:
            return self.focussed_thread.get_stackframe(self.focussed_frame_id)

    @property
    def scopes(self):
        return self.focussed_stackframe.scopes

    def update_scopes(self):
        print("scopes", [str(scope) for scope in self.scopes])

    def update_stacks(self):
        print("focussed frame: ", self.focussed_stackframe)

    def update_variables(self):
        print('variables')

    def update_threads(self):
        print("focussed thread: ", self.focussed_thread)


class DebugClient:

    def __init__(self):
        pass
