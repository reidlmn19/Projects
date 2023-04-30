class Paycheck:
    def __init__(self, path=None, employer=None, process=True):
        self.path = path
        self.employer = employer

        self.rawdata = None
        self.summary = {}
        if process:
            self.process()

    def process(self):
        self.get_rawdata()
        self.get_summary()

    def get_rawdata(self):
        print(f'Get raw data not defined for {self.employer}')

    def get_summary(self):
        print(f'Get summary not defined for {self.employer}')


class IRobotPaycheck(Paycheck):
    def __init__(self, path=None, employer='iRobot', process=True):
        super().__init__(path=path, employer=employer, process=process)


class ClearMotionPaycheck(Paycheck):
    def __init__(self, path=None, employer='ClearMotion', process=True):
        super().__init__(path=path, employer=employer, process=process)
