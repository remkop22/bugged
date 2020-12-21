from typing import List, Literal, Optional
from bugged.dap.messages import Event, Response
from bugged.dap.types import Source, SourceBreakpoint, Thread
from abc import ABC, abstractmethod

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

class ClientBase(ABC):

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
        self.sources: List[Source] = []
        self.process: Optional[Process] = None
        self.focussed_thread_id: Optional[int] = None
        self.focussed_frame_id: Optional[int] = None
        self.adapter: Optional['AdapterBase'] = None

    def add_source(self):
        source = Source()

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

    @abstractmethod
    def update_scopes(self):
        '''Gets called on changes to scopes'''
        pass

    @abstractmethod
    def update_stacks(self):
        '''Gets called on changes to stacks'''
        pass

    @abstractmethod
    def update_variables(self):
        '''Gets called on changes to variables'''
        pass

    @abstractmethod
    def update_threads(self):
        '''Gets called on changes to threads'''
        pass

    @abstractmethod
    def stopped(self, event: Event):
        '''Gets called when debugger sents "stopped" event'''
        pass

    @abstractmethod
    def continued(self, event: Event):
        '''Gets called when debugger sents "continued" event'''
        pass

    @abstractmethod
    def started(self, res: Response):
        '''Gets called when debugger responds to launch/attach request'''
        pass

    @abstractmethod
    def terminated(self, event: Event):
        '''Gets called when debugger sents "terminated" event'''
        pass

    @abstractmethod
    def initialize(self, res: Response):
        '''Gets called when the debugger responds the to the initialize request (requires the client to call attach/launch in order to proceed)'''
        pass

    @abstractmethod
    def configure(self, event: Event):
        '''Gets called when debugger sents "initialized" event, adapter will use the state of the client when this function returns to configure the debugger'''
        pass

class DebugClientBase:

    def __init__(self):
        pass
