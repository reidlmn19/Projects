class BettermentStatement:
    def __init__(self, path):
        self.path = path
        self.institution = 'Betterment'
        self.type = 'Statement'

    def read_data(self):
        return self.institution