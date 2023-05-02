from datetime import *
import pandas as pd
import PyPDF2
from StringTools import str_to_date, str_to_number, santander_transaction


class CardStatement:
    def __init__(self, path=None, account=None, institution=None, process=True):
        self.path = path
        self.account = account
        self.institution = institution

        self.rawdata = None
        self.summary = {}
        self.transactions = pd.DataFrame()
        if process:
            self.process()

    def process(self):
        raw_data = self.get_rawdata()
        self.get_summary(raw_data)
        self.get_transactions(raw_data)

    def get_summary(self):
        print(f'Get summary not defined for {self.institution}')

    def get_rawdata(self):
        print(f'Get raw data not defined for {self.institution}')

    def get_transactions(self):
        print(f'Get transactions not defined for {self.institution}')


class SantanderStatement(CardStatement):
    def __init__(self, path=None, account='Checking/Savings', institution='Santander', process=True):
        super().__init__(path=path, account=account, institution=institution, process=process)

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
            'Deposit Accounts Account Number Average Daily Balance Current Balance': 2
        }

        state = 1
        summary = {}
        for item in lst:
            item = item.strip()

            if state == 0:
                pass
            elif state == 1:
                if 'Statement Period' in item:
                    splt = item.split()
                    d1 = str_to_date(splt[2])
                    if d1 is not None:
                        summary['Period Starting'] = d1[0]
                    d2 = str_to_date(splt[4])
                    if d1 is not None:
                        summary['Period Ending'] = d2[0]
                state = 0
            elif state == 2:
                splt = item.split()
                n = str_to_number(splt[-1])
                if n is not None:
                    summary['Current Checking Balance'] = n
                state = 3
            elif state == 3:
                splt = item.split()
                n = str_to_number(splt[-1])
                if n is not None:
                    summary['Current Savings Balance'] = n
                state = 0

            if item in keywords.keys():
                last_keyword = item
                state = keywords[item]
                counter = 0

        summary['Institution'] = self.institution
        summary['Account'] = self.account
        self.summary = summary

    def get_transactions(self, debug=False):
        state = 0
        last_state = 0
        account = 'Checking'
        text_buffer = ''
        lst = self.rawdata.split('\n')
        entry_dic = {}

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
            elif state == 2:
                entry = santander_transaction(item, account=account)
                if entry is not None:
                    self.transactions = pd.concat([self.transactions,
                                                   pd.DataFrame(entry_dic, index=[0])], ignore_index=True)
                    text_buffer = ''
                elif len(text_buffer) > 0:
                    entry = santander_transaction(f'{text_buffer} {item}', account=account)
                    if entry is not None:
                        self.transactions = pd.concat([self.transactions,
                                                       pd.DataFrame(entry_dic, index=[0])], ignore_index=True)
                        text_buffer = ''
                else:
                    text_buffer = text_buffer + item
            elif state == 4:
                entry = santander_transaction(item, account=account)
                if entry is not None:
                    self.transactions = pd.concat([self.transactions,
                                                   pd.DataFrame(entry_dic, index=[0])], ignore_index=True)
                    text_buffer = ''
                elif len(text_buffer) > 0:
                    entry = santander_transaction(f'{text_buffer} {item}', account=account)
                    if entry is not None:
                        self.transactions = pd.concat([self.transactions,
                                                       pd.DataFrame(entry_dic, index=[0])], ignore_index=True)
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


class PeoplesStatement(CardStatement):
    def __init__(self, path=None, account='Checking', institution='Peoples', process=True):
        super().__init__(path=path, account=account, institution=institution, process=process)


class CapitalOneStatement(CardStatement):
    def __init__(self, path=None, account=None, institution='CapitalOne', process=True):
        super().__init__(path=path, account=account, institution=institution, process=process)

    def get_summary(self, lst, debug=False):
        if debug:
            print(lst)

        keywords = {
            'Previous Balance': 1,
            'Other Credits': 1,
            'Transactions': 1,
            'Cash Advances': 1,
            'Fees Charged': 1,
            'Interest Charged': 1,
            'New Balance': 1,
            'Credit Limit': 2,
            'Cash Advance Credit Limit': 1,
            'Available Credit for Cash Advances': 1,
            'Payment Due Date': 4,
            'Minimum Payment Due': 1,
            '  |  ': 5,
            'Visa Signature Account Ending in': 6,
            'Previous': 7,
            'Adjusted': 7,
            'Earned': 7,
            'Transferred In': 7,
            'Redeemed': 7,
            'Transferred Out': 7,
            'Rewards': 7,
            '-': 8
        }

        df = pd.DataFrame(columns=['Item', 'Flag'])
        state = 0
        last_keyword = ''
        last_item = ''
        summary = {}
        for item in lst:
            item = item.strip()
            s2d = str_to_date(item)
            s2n = str_to_number(item)

            if state == 0:
                pass
            elif state == 1:
                if s2n is not None:
                    summary[last_keyword] = s2n
                state = 0
            elif state == 2:
                if s2n is not None:
                    summary[last_keyword] = s2n
                state = 3
            elif state == 3:
                if s2n is not None:
                    summary['Available Credit'] = s2n
                state = 0
            elif state == 4:
                if s2d is not None:
                    summary[last_keyword] = s2d[0]
                state = 0
            elif state == 5:
                if s2n is not None:
                    summary['Days in Billing Cycle'] = s2n
                state = 0
            elif state == 6:
                if s2n is not None:
                    summary['Payments'] = s2n
                state = 0
            elif state == 7:
                if s2n is not None:
                    summary[f"{last_keyword} Earnings"] = s2n
                state = 0
            elif state == 8:
                if s2d is not None:
                    summary["Period Ending"] = s2d[0]
                    summary["Period Starting"] = p_start
                state = 0

            if item in keywords.keys():
                df = pd.concat([df, pd.DataFrame({'Item': item, 'Flag': keywords[item]}, index=[0])], ignore_index=True)
                state = keywords[item]
                last_keyword = item
                n = 0
                while last_keyword in summary.keys():
                    n += 1
                    last_keyword = item + str(n)
            elif s2d is not None:
                df = pd.concat([df, pd.DataFrame({'Item': item, 'Flag': s2d}, index=range(len(s2d)))],
                               ignore_index=True)
            elif s2n is not None:
                df = pd.concat([df, pd.DataFrame({'Item': item, 'Flag': s2n}, index=[0])], ignore_index=True)
            else:
                df = pd.concat([df, pd.DataFrame({'Item': item, 'Flag': None}, index=[0])], ignore_index=True)

            if state == 8:
                if str_to_date(last_item) is not None:
                    p_start = str_to_date(last_item)[0]
                else:
                    state = 0
            last_item = item

        if debug:
            df.to_csv('D:\Artifacts\Test.csv')
        summary['Account'] = self.account
        self.summary = summary

    def get_summary2(self, lst, debug=False):
        keywords = {
            'Previous Balance': 1,
            'Payments': 1,
            'Other Credits': 1,
            'Transactions': 1,
            'Cash Advances': 1,
            'Fees Charged': 1,
            'Interest Charged': 1,
            'New Balance': 1,
            'Credit Limit': 1,
            'Available Credit': 2,
            'Cash Advance Credit Limit': 1,
            'Available Credit for Cash Advances': 3,
            'Payment Due Date': 4,
            'days in Billing Cycle': 5
        }
        summary = {}
        last_key = ''
        state = 0
        for item in lst:
            for key in keywords.keys():
                if key in item:
                    state = keywords[key]
                    last_key = key

            if state == 0:
                pass
            elif state == 1:
                s2n = str_to_number(item.replace(last_key, ''))
                if s2n is not None:
                    summary[last_key] = s2n
                state = 0
            elif state == 2:
                s = item.replace(last_key, '').split(')')[1]
                s2n = str_to_number(s)
                if s2n is not None:
                    summary[last_key] = s2n
                state = 0
            elif state == 3:
                s = item.replace(last_key, '')
                s = s.replace('Payment Information', '')
                s2n = str_to_number(s)
                if s2n is not None:
                    summary[last_key] = s2n
                state = 0
            elif state == 4:
                # print(f'WTF do I do about {last_key} and {item}')
                state = 0
            elif state == 5:
                s = item.split(' | ')[0]
                s2d = str_to_date(s)
                if s2d is not None:
                    summary['Period Starting'] = s2d[0]
                    summary['Period Ending'] = s2d[1]
                state = 0

        summary['Account'] = self.account
        self.summary = summary

    def get_transactions(self, lst, debug=False):
        transactions = pd.DataFrame()
        state = 0
        next_entry = {}
        desc_buffer = ''
        for item in lst:
            s2d = str_to_date(item)
            s2n = str_to_number(item)

            if state == 0:
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
                if s2d is not None:
                    d = s2d[0]

                    if d.month == 1:
                        d = d.replace(year=self.summary['Period Ending'].year)
                    else:
                        d = d.replace(year=self.summary['Period Starting'].year)

                    next_entry['Date'] = d
                    state = 4
                else:
                    state = 3
            elif state == 4:
                if s2n is not None:
                    if '$' in item:
                        next_entry['Amount'] = s2n
                        next_entry['Description'] = desc_buffer
                        transactions = pd.concat([transactions, pd.DataFrame(next_entry, index=[0])], ignore_index=True)
                        desc_buffer = ''
                        next_entry = {}
                        state = 3
                    else:
                        desc_buffer = desc_buffer + item
                        state = 4
                else:
                    desc_buffer = desc_buffer + item
                    state = 4

            if item == "Date":
                state = 1
        if 'Period Ending' in self.summary.keys():
            transactions = pd.concat([transactions,
                                      pd.DataFrame({'Date': self.summary['Period Ending'],
                                                    'Description': 'Interest Charged',
                                                    'Amount': self.summary['Interest Charged']
                                                    }, index=[0])], ignore_index=True)
        transactions['Account'] = self.account
        transactions.Amount = transactions.Amount * -1
        self.transactions = transactions
        if debug:
            transactions.to_csv('D:\Artifacts\Test2.csv')

    def get_transactions2(self, lst, debug=False):
        transactions = pd.DataFrame()
        state = 0
        next_entry = {}
        for item in lst:
            if state == 0:
                pass
            elif state == 1:
                item = item.strip()
                cells = item.split(' ')
                if str_to_date(' '.join(cells[0:2])) is None:
                    continue
                t_date = ' '.join(cells[0:2])
                p_date = ' '.join(cells[2:4])
                if cells[-2] in ['+', '-']:
                    desc = ' '.join(cells[4:-2])
                    amt = ' '.join(cells[-2:])
                else:
                    desc = ' '.join(cells[4:-1])
                    amt = ' '.join(cells[-1:])

                t_date = str_to_date(t_date)[0]
                p_date = str_to_date(p_date)[0]
                amt = str_to_number(amt)

                if t_date.month == 1:
                    t_date = t_date.replace(year=self.summary['Period Ending'].year)
                else:
                    t_date = t_date.replace(year=self.summary['Period Starting'].year)
                if p_date.month == 1:
                    p_date = p_date.replace(year=self.summary['Period Ending'].year)
                else:
                    p_date = p_date.replace(year=self.summary['Period Starting'].year)

                new_entry = {
                    'Post Date': p_date,
                    'Transaction Date': t_date,
                    'Date': p_date,
                    'Amount': amt,
                    'Description': desc
                }
                if None in new_entry.values():
                    continue
                # elif np.isnan(new_entry['Date']):
                #     continue
                transactions = pd.concat([transactions,
                                          pd.DataFrame(new_entry, index=[0])], ignore_index=True)

            if item == "Trans Date Post Date Description Amount ":
                state = 1

        if 'Period Ending' in self.summary.keys():
            transactions = pd.concat([transactions,
                                      pd.DataFrame({'Date': self.summary['Period Ending'],
                                                    'Description': 'Interest Charged',
                                                    'Amount': self.summary['Interest Charged']
                                                    }, index=[0])], ignore_index=True)
        transactions['Account'] = self.account
        transactions.Amount = transactions.Amount * -1
        self.transactions = transactions
        if debug:
            transactions.to_csv('D:\Artifacts\Test2.csv')

    def get_rawdata(self, debug=False):
        pages_list = []
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extract_text()
            page_list = page_text.split('\n')
            pages_list.extend(page_list)
        self.rawdata = pages_list
