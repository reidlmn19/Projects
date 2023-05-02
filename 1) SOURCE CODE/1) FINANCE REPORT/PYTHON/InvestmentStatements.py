import pandas as pd
import PyPDF2
from StringTools import str_to_date, str_to_number


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
        pages_text = ''
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extract_text()
            pages_text = pages_text + page_text
        self.rawdata = pages_text

    def get_summary(self, debug=False):
        lst = self.rawdata.split('\n')
        if debug:
            print(lst)

        keywords = {
            'Quarterly Statement': 1,
            'CURRENT BALANCE': 2,
            'Total invested': 3,
            'Total earned': 4,
            'Vested balance': 5,
            'Stocks': 6,
            'Bonds': 7,
            'Total': 8,
            'All 401(k) Holdings': 9
        }

        state = 0
        last_keyword = ''
        summary = {}
        counter = 0
        for item in lst:
            item = item.strip()
            s2d = str_to_date(item)
            s2n = str_to_number(item)

            if state == 0:
                pass
            elif state == 1:
                item = item.replace('1st', '1')
                item = item.replace('2nd', '2')
                item = item.replace('3rd', '3')
                item = item.replace('th', '')
                items = item.split('-')
                d1 = str_to_date(items[0].strip())
                d2 = str_to_date(items[1].strip())
                if d1 is not None:
                    summary['Period Start'] = d1[0]
                if d2 is not None:
                    summary['Period End'] = d2[0]
                state = 0
            elif state == 2:
                if s2n is not None:
                    summary['Current Balance'] = s2n
                    state = 0
            elif state == 3:
                if s2n is not None:
                    summary['Total Invested'] = s2n
                    state = 0
            elif state == 4:
                if s2n is not None:
                    summary['Total Earned'] = s2n
                    state = 0
            elif state == 5:
                if s2n is not None:
                    summary['Vested Balance'] = s2n
                    state = 0
            elif state == 6:
                ks = [f'Previous {last_keyword} Balance', f'{last_keyword} Change',
                      f'Current {last_keyword} Value', f'{last_keyword} Balance Composition']
                if s2n is not None:
                    summary[ks[counter]] = s2n
                    counter += 1
            elif state == 7:
                ks = [f'Previous {last_keyword} Balance', f'{last_keyword} Change',
                      f'Current {last_keyword} Value', f'{last_keyword} Balance Composition']
                if s2n is not None:
                    summary[ks[counter]] = s2n
                    counter += 1
            elif state == 8:
                ks = [f'Previous {last_keyword} Balance', f'{last_keyword} Change',
                      f'Current {last_keyword} Value', f'{last_keyword} Balance Composition']
                if s2n is not None:
                    summary[ks[counter]] = s2n
                    counter += 1
            elif state == 9:
                break

            if item in keywords.keys():
                last_keyword = item
                state = keywords[item]
                counter = 0

        summary['Broker'] = self.broker
        self.summary = summary
