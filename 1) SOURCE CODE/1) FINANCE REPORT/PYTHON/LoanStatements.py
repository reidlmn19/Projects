from datetime import *
from tabulate import tabulate
import pandas as pd
import numpy as np
import PyPDF2
from StringTools import str_to_date, str_to_number


def santander_transaction(s, account=None, years=None):
    df = pd.DataFrame()
    if 'Account Activity (Cont. for Acct#' in s:
        s = s.split('Page')[0]
    lst = s.split()
    if len(lst) > 3:
        try:
            df.at[0, 'Date'] = str_to_date(lst[0])[0]
            df.at[0, 'Description'] = ' '.join(lst[1:-2])
            df.at[0, 'Amount'] = str_to_number(lst[-2])
            df.at[0, 'Balance'] = str_to_number(lst[-1])

            if account is not None:
                df.at[0, 'Account'] = account

            if years is not None:
                if df.at[0, 'Date'].month == 1:
                    df.at[0, 'Date'] = df.at[0, 'Date'].replace(year=years[1])
                else:
                    df.at[0, 'Date'] = df.at[0, 'Date'].replace(year=years[0])
        except:
            return None
        if df.isnull().values.any():
            return None
        else:
            return df


class LoanStatement:
    def __init__(self, path=None, account=None, institution=None, process=True):
        self.path = path
        self.account = account
        self.institution = institution
        self.result = 'Incomplete'

        self.rawdata = None
        self.summary = {}
        self.transactions = pd.DataFrame()
        if process:
            self.process()

    def process(self):
        try:
            self.get_rawdata()
            self.get_summary()
            self.result = self.health_check()
        except Exception as e:
            print(f'File Extraction Failed: {self.path} {e}')
            self.result = 'Failed'

    def get_rawdata(self):
        pages_text = ''
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extract_text()
            pages_text = pages_text + page_text
        self.rawdata = pages_text

    def get_summary(self):
        self.summary = {'Starting Balance': None,
                        'Ending Balance': None,
                        'Starting Date': None,
                        'Ending Date': None}

    def get_transactions(self):
        self.transactions = pd.DataFrame()

    def health_check(self):
        if self.summary['Starting Date'] is None:
            return 'No Date'
        if self.summary['Ending Date'] is None:
            return 'No Date'
        if self.transactions.empty:
            return 'No Transactions'
        return 'Success'


class NelnetStatement(LoanStatement):
    def __init__(self, path=None, account='Student', institution='Nelnet', process=True):
        super().__init__(path=path, account='Student', institution=institution, process=process)

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

    def fix_amount_signs(self):
        check_balance = pd.DataFrame({'Date': self.summary['Starting Date'],
                                      'Description': 'Ignore',
                                      'Amount': 0,
                                      'Balance': self.summary['Starting Balance Checking'],
                                      'Account': 'Checking'}, index=[0])
        save_balance = pd.DataFrame({'Date': self.summary['Starting Date'],
                                     'Description': 'Ignore',
                                     'Amount': 0,
                                     'Balance': self.summary['Starting Balance Savings'],
                                     'Account': 'Savings'}, index=[0])
        self.transactions = pd.concat([check_balance, save_balance, self.transactions]).reset_index(drop=True)

        df1 = self.transactions.set_index('Date')
        df1 = df1[df1['Account'] == 'Checking']
        df1['Sign1'] = df1['Balance'].diff() < 0
        df1['Amount'] = np.where(df1['Sign1'], -df1['Amount'], df1['Amount'])

        df2 = self.transactions.set_index('Date')
        df2 = df2[df2['Account'] == 'Savings']
        df2['Sign2'] = df2['Balance'].diff() < 0
        df2['Amount'] = np.where(df2['Sign2'], -df2['Amount'], df2['Amount'])

        self.transactions = pd.concat([df1, df2]).drop(columns=['Sign1', 'Sign2'])
        self.transactions = self.transactions.drop(self.transactions[self.transactions['Amount'] == 0].index)
        self.transactions.reset_index(inplace=True)
