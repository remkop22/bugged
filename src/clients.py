from dataclasses import dataclass

class Client:

    def __init__(self, clientID: str, clientName: str, locale: str):
        self.clientID = clientID
        self.clientName = clientName
        self.locale = locale

        self.linesStartAt1 = False
        self.columnsStartAt1 = False

        self.pathFormat = 'path'

        self.supportsVariableType = False
        self.supportsVariablePaging = False
        self.supportsRunInTerminalRequest = False
        self.supportsMemoryReferences = False
        self.supportsProgressReporting = False
        self.supportsInvalidatedEvent = False

class DebugClient:

    def __init__(self):
        pass
