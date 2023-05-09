from datetime import *
from tabulate import tabulate
import pandas as pd
import numpy as np
import PyPDF2
from StringTools import str_to_date, str_to_number


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

    def get_rawdata(self, debug=False):
        pages_text = ''
        reader = PyPDF2.PdfFileReader(self.path)
        print(len(reader.pages))
        for page in reader.pages:
            page_text = page.extract_text()
            pages_text = pages_text + page_text
        self.rawdata = pages_text

    def get_summary(self, debug=False):
        lst = self.rawdata.split('\n')
        state = 0
        last_state = 0
        last_item = ''
        date_range = None

        if debug:
            print(lst)

        keywords = {
            'STUDENT VALUE CHECKING Statement Period': 1,
            'Balances': 2,
            'SANTANDER SAVINGS Statement Period': 3
        }

        for item in lst:
            item = item.strip()

            if state == 0:
                pass
            elif state == 1:
                splt = last_item.replace('STUDENT VALUE CHECKING Statement Period ', '').split()
                d1 = str_to_date(splt[0])
                d2 = str_to_date(splt[-1])
                if d1 is not None:
                    self.summary['Starting Date'] = d1[0]
                if d2 is not None:
                    self.summary['Ending Date'] = d2[0]
            elif state == 2:
                if last_state == 1:
                    if 'Beginning Balance ' in item:
                        a1 = str_to_number(item.replace('Beginning Balance ', '').split()[0])
                        if a1 is not None:
                            self.summary['Starting Balance Checking'] = a1
                    if 'Current Balance' in item:
                        a2 = str_to_number(item.split()[-1])
                        if a2 is not None:
                            self.summary['Ending Balance Checking'] = a2
                elif last_state == 3:
                    if 'Beginning Balance ' in item:
                        a1 = str_to_number(item.replace('Beginning Balance ', '').split()[0])
                        if a1 is not None:
                            self.summary['Starting Balance Savings'] = a1
                    if 'Current Balance' in item:
                        a2 = str_to_number(item.split()[-1])
                        if a2 is not None:
                            self.summary['Ending Balance Savings'] = a2
                last_state = state
                state = 0

            for key in keywords.keys():
                if key in item:
                    last_state = state
                    state = keywords[key]
                    last_item = item

    def get_transactions(self, debug=False):
        yr_rng = [self.summary['Starting Date'].year, self.summary['Ending Date'].year]
        state = 0
        last_state = 0
        account = 'Checking'
        text_buffer = ''
        lst = self.rawdata.split('\n')

        if debug:
            print(lst)

        keywords = {
            'Date Description Additions Subtractions Balance': 1,
            'Ending Balance': 3,
        }

        for item in lst:
            item = item.strip()

            if state == 0:
                pass
            elif state == 1:
                if 'Beginning Balance' in item:
                    if last_state == 0:
                        state = 2
                    elif last_state == 3:
                        state = 4
                elif last_state == 2:
                    state = 2
                elif last_state == 4:
                    state = 4
            elif state == 2:
                entry = item
                if entry is not None:
                    self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                    text_buffer = ''
                elif len(text_buffer) > 0:
                    entry = item
                    if entry is not None:
                        self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                        text_buffer = ''
                else:
                    text_buffer = text_buffer + item
            elif state == 3:
                if last_state == 4:
                    break
                else:
                    account = 'Savings'
                    text_buffer = ''
            elif state == 4:
                entry = santander_transaction(item, account=account, years=yr_rng)
                if entry is not None:
                    self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                    text_buffer = ''
                elif len(text_buffer) > 0:
                    entry = santander_transaction(f'{text_buffer} {item}'.replace('$', ' '),
                                                  account=account, years=yr_rng)
                    if entry is not None:
                        self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                        text_buffer = ''
                else:
                    text_buffer = text_buffer + item

            if item in keywords.keys():
                last_state = state
                state = keywords[item]
            else:
                for key in keywords.keys():
                    if key in item:
                        last_state = state
                        state = keywords[key]
        self.fix_amount_signs()
        self.transactions['Institution'] = self.institution
