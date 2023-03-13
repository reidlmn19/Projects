class SantanderStatement:
    def __init__(self, path):
        self.path = path
        self.institution = 'Santander'
        self.type = 'Statement'

    def read_data(self):
        return self.institution