from bugged.base import ClientBase
from bugged.dap.messages import Event, Response

class GenericClient(ClientBase):

    def __init__(self):
        super().__init__('bugged_generic_client', 'BuggedGenericClient', 'en_US')
        self.configuration['supportsVariableType'] = True
        self.configuration['supportsVariablePaging'] = True

    def update_scopes(self):
        pass

    def update_stacks(self):
        pass

    def update_threads(self):
        pass

    def update_variables(self):
        pass

    def started(self, res: Response):
        pass

    def stopped(self, event: Event):
        print('stopped')

    def continued(self, event: Event):
        pass

    def terminated(self, event: Event):
        pass

    def initialize(self, res: Response):
        self.adapter.attach()

    def configure(self, event: Event):
        pass
