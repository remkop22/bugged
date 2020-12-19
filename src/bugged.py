from adapter import AdapterBase

class BuggedAdapter(AdapterBase):

    def __init__(self, address, client):
        super().__init__(address, 'bugged', client)
