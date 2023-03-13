class FidelityStatement:
    def __init__(self, path):
        self.path = path
        self.institution = 'Fidelity'
        self.type = 'Statement'

    def read_data(self):
        return self.institution