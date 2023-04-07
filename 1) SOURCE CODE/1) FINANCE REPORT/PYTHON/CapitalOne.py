from datetime import *
import pandas as pd
import PyPDF2
import numpy as np


def str_to_date(s, year=None):
    formats = [
        '%b. %d, %Y',
        '%b %d, %Y',
        '%b %d',
        '%d-%b'
    ]
    for f in formats:
        try:
            d = datetime.strptime(s, f)
            if year:
                d = d.replace(year=year)
            return [d]
        except:
            pass
    if len(s) >= 10:
        try:
            split = s.split(' - ')
            d1 = split[0].strip()
            d2 = split[1].strip()
            if '.' in d1:
                d = [datetime.strptime(d1, '%b. %d, %Y'), datetime.strptime(d2, '%b. %d, %Y')]
            else:
                d = [datetime.strptime(d1, '%b %d, %Y'), datetime.strptime(d2, '%b %d, %Y')]
            return d
        except:
            pass
    return None


def str_to_number(s):
    pos = False
    neg = False
    if '$' in s:
        s = s.replace('$', '')
    if ',' in s:
        s = s.replace(',', '')
    if '=' in s:
        s = s.replace('=', '')
    if '+' in s:
        s = s.replace('+', '')
        pos = True
    elif '-' in s:
        s = s.replace('-', '')
        neg = True
    s.strip()
    try:
        num = float(s)
        if pos:
            num = abs(num)
        elif neg:
            num = abs(num) * -1
        return num
    except:
        pass


class CapitalOneStatement:
    def __init__(self, path, account=None):
        self.path = path
        self.institution = 'CapitalOne'
        self.type = 'Statement'
        if account is None:
            self.account = 'Unknown'
        else:
            self.account = account

        self.summary = {}
        self.transactions = pd.DataFrame()

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

    def read_data(self, debug=False):
        pages_list = []
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extractText()
            page_list = page_text.split('\n')
            pages_list.extend(page_list)

        try:
            self.get_summary2(pages_list, debug=debug)
            self.get_transactions2(pages_list, debug=debug)
        except:
            print(f'Failed once: {self.path}')

        if len(self.transactions)<2:
            try:
                self.get_summary(pages_list, debug=debug)
                self.get_transactions(pages_list, debug=debug)
            except:
                print(f'Failed twice: {self.path}')