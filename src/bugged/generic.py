from bugged.base import ClientBase

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

    def started(self):
        pass

    def stopped(self):
        pass

    def continued(self):
        pass

    def terminated(self):
        pass
