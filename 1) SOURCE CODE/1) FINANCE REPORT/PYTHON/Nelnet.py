class NelnetStatement:
    def __init__(self, path):
        self.path = path
        self.institution = 'Nelnet'
        self.type = 'Statement'

    def read_data(self):
        return self.institution