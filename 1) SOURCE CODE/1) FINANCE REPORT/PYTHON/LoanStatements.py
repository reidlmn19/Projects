class LoanStatement:
    def __init__(self, path=None, lender=None, process=True):
        self.path = path
        self.lender = lender

        self.rawdata = None
        self.summary = {}
        if process:
            self.process()

    def process(self):
        self.get_rawdata()
        self.get_summary()

    def get_rawdata(self):
        print(f'Get raw data not defined for {self.lender}')

    def get_summary(self):
        print(f'Get summary not defined for {self.lender}')


class NelnetStatement(LoanStatement):
    def __init__(self, path=None, lender=None, process=True):
        super().__init__(path=path, lender=lender, process=process)