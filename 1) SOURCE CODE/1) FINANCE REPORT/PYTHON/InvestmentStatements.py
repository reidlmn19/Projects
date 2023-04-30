import PyPDF2

class InvestmentStatement:
    def __init__(self, path=None, broker=None, process=True):
        self.path = path
        self.broker = broker

        self.rawdata = None
        self.summary = {}
        if process:
            self.process()

    def process(self):
        self.get_rawdata()
        self.get_summary()

    def get_rawdata(self):
        print(f'Get raw data not defined for {self.broker}')

    def get_summary(self):
        print(f'Get summary not defined for {self.broker}')


class FidelityStatement(InvestmentStatement):
    def __init__(self, path=None, broker='Fidelity', process=True):
        super().__init__(path=path, broker=broker, process=process)


class BettermentStatement(InvestmentStatement):
    def __init__(self, path=None, broker='Betterment', process=True):
        super().__init__(path=path, broker=broker, process=process)

    def get_rawdata(self, debug=False):
        pages_list = []
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extract_text()
            page_list = page_text.split('\n')
            pages_list.extend(page_list)
        self.rawdata = pages_list
