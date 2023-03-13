class iRobotPaycheck:
    def __init__(self, path):
        self.path = path
        self.institution = 'iRobot'
        self.type = 'Paycheck'

    def read_data(self):
        return self.institution