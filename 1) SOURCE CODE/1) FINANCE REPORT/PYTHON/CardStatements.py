from datetime import *
from tabulate import tabulate
import pandas as pd
import numpy as np
import PyPDF2
from StringTools import str_to_date, str_to_number


# For every card statement you need a summary including start date, end date,
# starting balance, and ending balance (for each account on the statement)
# The transaction table requires a Date, Amount, and Description. A Ledger is preferred but
# not necessary

def capitalone_transaction(s, account=None, years=None):
    df = pd.DataFrame()
    if 'Account Activity (Cont. for Acct#' in s:
        s = s.split('Page')[0]
    lst = s.split()
    if len(lst) > 5:
        try:
            df.at[0, 'Transaction Date'] = str_to_date(' '.join(lst[0:2]))[0]
            df.at[0, 'Post Date'] = str_to_date(' '.join(lst[2:4]))[0]
            df.at[0, 'Amount'] = str_to_number(lst[-1])
            if lst[-2] == '-':
                df.at[0, 'Amount'] = df.at[0, 'Amount'] * -1
                df.at[0, 'Description'] = ' '.join(lst[4:-2])
            else:
                df.at[0, 'Description'] = ' '.join(lst[4:-1])

            if account is not None:
                df.at[0, 'Account'] = account

            if years is not None:
                if df.at[0, 'Post Date'].month == 1:
                    df.at[0, 'Post Date'] = df.at[0, 'Post Date'].replace(year=years[1])
                else:
                    df.at[0, 'Post Date'] = df.at[0, 'Post Date'].replace(year=years[0])

                if df.at[0, 'Transaction Date'].month == 1:
                    df.at[0, 'Transaction Date'] = df.at[0, 'Transaction Date'].replace(year=years[1])
                else:
                    df.at[0, 'Transaction Date'] = df.at[0, 'Transaction Date'].replace(year=years[0])

        except:
            return None
        if df.isnull().values.any():
            return None
        else:
            return df


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


class CardStatement:
    def __init__(self, path=None, account=None, institution=None, process=True, safe_mode=True):
        self.path = path
        self.account = account
        self.institution = institution
        self.result = 'Incomplete'

        self.rawdata = None
        self.summary = {}
        self.transactions = pd.DataFrame()
        if process:
            self.process(safe_mode=safe_mode)

    def process(self, safe_mode=True):
        if safe_mode:
            try:
                self.get_rawdata()
                self.get_summary()
                self.get_transactions()
                self.result = 'Success'
            except Exception as e:
                print(f'File Extraction Failed: {self.path} {e}')
                self.result = 'Failed'
        else:
            self.get_rawdata()
            self.get_summary()
            self.get_transactions()
            self.result = 'Success'

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
        self.transactions = None


class SantanderStatement(CardStatement):
    def __init__(self, path=None, account='Checking/Savings', institution='Santander', process=True, safe_mode=True):
        self.savings = CardStatement(path=path, account='Savings', institution='Santander', process=False,
                                     safe_mode=safe_mode)
        self.checking = CardStatement(path=path, account='Checking', institution='Santander', process=False,
                                      safe_mode=safe_mode)
        super().__init__(path=path, account=account, institution=institution, process=process, safe_mode=safe_mode)
        self.savings.result = self.checking.result = 'Success'

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
            'SANTANDER SAVINGS Statement Period': 3,
        }

        if 'Statement Period ' in lst[0]:
            splt = lst[0].replace('Statement Period ', '').split(' TO ')
            d1 = str_to_date(splt[0])
            d2 = str_to_date(splt[-1])
            if d1 is not None:
                self.checking.summary['Starting Date'] = self.savings.summary['Starting Date'] = d1[0]
            if d2 is not None:
                self.checking.summary['Ending Date'] = self.savings.summary['Ending Date'] = d2[0]

        for item in lst:
            item = item.strip()

            if state == 0:
                pass
            elif state == 1:
                splt = last_item.replace('STUDENT VALUE CHECKING Statement Period ', '').split()
                d1 = str_to_date(splt[0])
                d2 = str_to_date(splt[-1])
                if d1 is not None:
                    self.checking.summary['Starting Date'] = self.savings.summary['Starting Date'] = d1[0]
                if d2 is not None:
                    self.checking.summary['Ending Date'] = self.savings.summary['Ending Date'] = d2[0]
            elif state == 2:
                if last_state == 1:
                    if 'Beginning Balance ' in item:
                        a1 = str_to_number(item.replace('Beginning Balance ', '').split()[0])
                        if a1 is not None:
                            self.checking.summary['Starting Balance'] = a1
                    if 'Current Balance' in item:
                        a2 = str_to_number(item.split()[-1])
                        if a2 is not None:
                            self.checking.summary['Ending Balance'] = a2
                elif last_state == 3:
                    if 'Beginning Balance ' in item:
                        a1 = str_to_number(item.replace('Beginning Balance ', '').split()[0])
                        if a1 is not None:
                            self.savings.summary['Starting Balance'] = a1
                    if 'Current Balance' in item:
                        a2 = str_to_number(item.split()[-1])
                        if a2 is not None:
                            self.savings.summary['Ending Balance'] = a2
                last_state = state
                state = 0

            for key in keywords.keys():
                if key in item:
                    last_state = state
                    state = keywords[key]
                    last_item = item

    def get_transactions(self, debug=False):
        yr_rng = [self.checking.summary['Starting Date'].year, self.checking.summary['Ending Date'].year]
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
            elif state == 3:
                if last_state == 4:
                    break
                else:
                    account = 'Savings'
                    yr_rng = [self.savings.summary['Starting Date'].year, self.savings.summary['Ending Date'].year]
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
        self.checking.transactions = self.transactions[self.transactions['Account'] == self.checking.account]
        self.savings.transactions = self.transactions[self.transactions['Account'] == self.savings.account]

    def fix_amount_signs(self):
        check_balance = pd.DataFrame({'Date': self.checking.summary['Starting Date'],
                                      'Description': 'Ignore',
                                      'Amount': 0,
                                      'Balance': self.checking.summary['Starting Balance'],
                                      'Account': self.checking.account}, index=[0])
        save_balance = pd.DataFrame({'Date': self.savings.summary['Starting Date'],
                                     'Description': 'Ignore',
                                     'Amount': 0,
                                     'Balance': self.savings.summary['Starting Balance'],
                                     'Account': self.savings.account}, index=[0])
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


class PeoplesStatement(CardStatement):
    def __init__(self, path=None, account='Checking', institution='Peoples', process=True):
        super().__init__(path=path, account=account, institution=institution, process=process)

    def get_rawdata(self):
        self.rawdata = None


class CapitalOneStatement(CardStatement):
    def __init__(self, path=None, account=None, institution='CapitalOne', process=True):
        super().__init__(path=path, account=account, institution=institution, process=process)

    def process(self, safe_mode=True):
        if safe_mode:
            try:
                self.get_rawdata()
                self.get_summary()
                if self.summary['Starting Date'] >= datetime(year=2022, month=1, day=1):
                    self.get_transactions()
                else:
                    self.get_transactions_old()
                self.result = 'Success'
            except:
                print(f'File Extraction Failed: {self.path}')
                self.result = 'Failed'
        else:
            self.get_rawdata()
            self.get_summary()
            if self.summary['Starting Date'] >= datetime(year=2022, month=1, day=1):
                self.get_transactions()
            else:
                self.get_transactions_old()
            self.result = 'Success'

    def get_summary(self, debug=False):
        lst = self.rawdata.split('\n')
        state = 0
        counter = 0
        last_key = ''

        if debug:
            print(lst)

        keywords = {
            'Previous Balance': 1,
            'New Balance': 2,
            'days in Billing Cycle': 3,
            'Credit Limit': 4,
            'Rewards Balance': 5,
            'Previous Balance Earned This Period Redeemed this period': 6,
        }

        for item in lst:
            item = item.strip()

            for key in keywords.keys():
                if key in item:
                    last_key = key
                    state = keywords[key]
                elif item == 'Rewards':
                    state = 7
                elif item == '|':
                    state = 8
                elif item == 'Previous':
                    state = 9

            if state == 0:
                pass
            elif state == 1:
                if item == last_key:
                    counter += 1
                    continue
                splt = item.replace(last_key, '').split()
                if len(splt) < 2:
                    n = str_to_number(item.replace(last_key, ''))
                else:
                    n = str_to_number(splt[-1])
                if n is not None:
                    self.summary['Starting Balance'] = n
                state = 0
            elif state == 2:
                if item == last_key:
                    counter += 1
                    continue
                n = str_to_number(item)
                if n is not None:
                    self.summary['Ending Balance'] = n
                else:
                    splt = item.replace(last_key, '').split()
                    if len(splt) < 2:
                        n = str_to_number(item.replace(last_key, ''))
                    else:
                        n = str_to_number(splt[-1])
                    if n is not None:
                        self.summary['Ending Balance'] = n
                state = 0
            elif state == 3:
                splt = item.split(' | ')
                if len(splt) < 2:
                    pass
                else:
                    dates = splt[0].split(' - ')
                    d1 = str_to_date(dates[0].strip())
                    if d1 is not None:
                        self.summary['Starting Date'] = d1[0]
                    d2 = str_to_date(dates[1].strip())
                    if d1 is not None:
                        self.summary['Ending Date'] = d2[0]
                state = 0
            elif state == 4:
                if item == last_key:
                    counter += 1
                    continue
                if 'Cash Advance' in item:
                    pass
                else:
                    splt = item.replace(last_key, '').split()
                    if len(splt) < 2:
                        n = str_to_number(item.replace(last_key, ''))
                    else:
                        n = str_to_number(splt[-1])
                    if n is not None:
                        self.summary['Credit Limit'] = n
                state = 0
            elif state == 5:
                if last_key in item:
                    pass
                else:
                    splt = item.split()
                    n = str_to_number(splt[0])
                    if n is not None:
                        self.summary['Ending Rewards Balance'] = n
                    state = 0
            elif state == 6:
                if last_key in item:
                    counter += 1
                    continue
                else:
                    splt = item.split()
                    n1 = str_to_number(splt[0])
                    if n1 is not None:
                        self.summary['Starting Rewards Balance'] = n1
                    state = 0
            elif state == 7:
                n = str_to_number(lst[counter + 1])
                if n is not None:
                    self.summary['Ending Rewards Balance'] = n
                else:
                    state = 0
            elif state == 8:
                s = ' '.join(lst[counter - 3:counter])
                splt = s.split('-')
                if len(splt) > 1:
                    d1 = str_to_date(splt[0].strip())
                    if d1 is not None:
                        self.summary['Starting Date'] = d1[0]
                    d2 = str_to_date(splt[1].strip())
                    if d2 is not None:
                        self.summary['Ending Date'] = d2[0]
                state = 0
            elif state == 9:
                if 'Earnings as of' in lst[counter - 1]:
                    n = str_to_number(lst[counter + 1])
                    if n is not None:
                        self.summary['Starting Rewards Balance'] = n
                state = 0
            counter += 1

    def get_transactions(self, debug=False):
        yr_rng = [self.summary['Starting Date'].year, self.summary['Ending Date'].year]
        state = 0
        text_buffer = ''
        last_item = ''
        lst = self.rawdata.split('\n')

        if debug:
            print(lst)

        keywords = {
            'Trans Date Post Date Description Amount': 1,
            'Total Interest for This Period': 2,
        }

        for item in lst:
            item = item.strip()

            if state == 0:
                pass
            elif state == 1:
                entry = capitalone_transaction(item, years=yr_rng)
                if entry is not None:
                    self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                    text_buffer = ''
                elif len(text_buffer) > 0:
                    entry = capitalone_transaction(f'{text_buffer} {item}'.replace('$', ' '), years=yr_rng)
                    if entry is not None:
                        self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                        text_buffer = ''
                else:
                    text_buffer = text_buffer + item
            elif state == 2:
                splt = last_item.split()
                n = str_to_number(splt[-1])
                if n is not None:
                    entry = pd.DataFrame({'Post Date': self.summary['Ending Date'],
                                          'Transaction Date': self.summary['Ending Date'],
                                          'Description': 'Interest Charge',
                                          'Amount': n}, index=[0])
                    self.transactions = pd.concat([self.transactions, entry], ignore_index=True)
                state = 0

            for key in keywords.keys():
                if key in item:
                    state = keywords[key]
                    text_buffer = ''
                    last_item = item
        self.transactions['Institution'] = self.institution
        self.transactions['Account'] = self.account
        self.transactions['Date'] = self.transactions['Post Date']
        self.transactions = self.transactions.drop(columns=['Post Date', 'Transaction Date'])

    def get_transactions_old(self, debug=False):
        yr_rng = [self.summary['Starting Date'].year, self.summary['Ending Date'].year]
        state = 0
        entry = {}
        text_buffer = ''
        lst = self.rawdata.split('\n')

        if debug:
            print(lst)

        keywords = {
            'Total Interest charged': 4
        }

        for item in lst:
            item = item.strip()

            if state == 0:
                if item == 'Date':
                    state = 1
                else:
                    pass
            elif state == 1:
                if item == 'Description':
                    state = 2
                else:
                    state = 0
            elif state == 2:
                if item == 'Amount':
                    state = 3
                else:
                    state = 0
            elif state == 3:
                n = str_to_number(item)
                if 'Date' not in entry.keys():
                    d = str_to_date(item)
                    if d is not None:
                        if d[0].month == 1:
                            d[0] = d[0].replace(year=yr_rng[1])
                        else:
                            d[0] = d[0].replace(year=yr_rng[0])
                        entry['Date'] = d[0]
                elif n is not None:
                    entry['Amount'] = n
                    entry['Description'] = text_buffer
                    self.transactions = pd.concat([self.transactions, pd.DataFrame(entry, index=[0])],
                                                  ignore_index=True)
                    text_buffer = ''
                    entry = {}
                else:
                    text_buffer = f'{text_buffer} {item}'
            elif state == 4:
                n = str_to_number(item)
                if n is not None:
                    entry['Amount'] = n
                    entry['Date'] = self.summary['Ending Date']
                    entry['Description'] = 'Interest Charge'
                    self.transactions = pd.concat([self.transactions, pd.DataFrame(entry, index=[0])],
                                                  ignore_index=True)
                    entry = {}
                state = 0

            for key in keywords.keys():
                if key in item:
                    state = keywords[key]
                    text_buffer = ''
                    last_item = item

        self.transactions['Institution'] = self.institution
        self.transactions['Account'] = self.account
