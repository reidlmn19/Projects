import matplotlib.pyplot as plt
import pandas as pd
import os
import win32api
import datetime

from CardStatements import CapitalOneStatement, SantanderStatement, PeoplesStatement, CardStatement
from InvestmentStatements import FidelityStatement, BettermentStatement, InvestmentStatement
from LoanStatements import NelnetStatement, LoanStatement
from Paychecks import IRobotPaycheck, ClearMotionPaycheck, Paycheck

right_now = datetime.date.today()


def get_data_from_file(path, process=True):
    obj = None
    if os.path.exists(path):
        if 'betterment' in path.lower():
            obj = BettermentStatement(path, process=process)
        elif 'santander' in path.lower():
            obj = SantanderStatement(path, process=process)
        elif 'peoples' in path.lower():
            obj = PeoplesStatement(path, process=process)
        elif 'quicksilver' in path.lower():
            obj = CapitalOneStatement(path, account='Quicksilver', process=process)
        elif 'platinum' in path.lower():
            obj = CapitalOneStatement(path, account='Platinum', process=process)
        elif 'nelnet' in path.lower():
            obj = NelnetStatement(path, process=process)
        elif 'irobot' in path.lower():
            obj = IRobotPaycheck(path, process=process)
        elif 'fidelity' in path.lower():
            obj = FidelityStatement(path, process=process)
        elif 'clearmotion' in path.lower():
            obj = ClearMotionPaycheck(path, process=process)
    else:
        print(f'Path invalid: {path}')
    return obj


def finddirectory(keyword='FINANCE'):
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for i in drives:
        d = win32api.GetVolumeInformation(i)
        if keyword.lower() == d[0].lower():
            return i
    return None


class FinanceManager:
    def __init__(self, title=None, path=None, bool_debug=False):
        if path is None:
            self.path = finddirectory()
        else:
            self.path = path

        if title is None:
            self.title = f'Finance Report - {right_now}'
        else:
            self.title = title

        if self.path is not None:
            self.path_rawData = r'\\'.join([self.path, 'RawData\\'])

            self.path_artifacts = r'\\'.join([self.path, 'Artifacts\\'])
            self.path_report = f'{self.path_artifacts}\\{self.title}'

            self.path_permData = r'\\'.join([self.path, 'PermanentData\\'])
            self.path_dataReg = f'{self.path_permData}\\DataRegistry.csv'
            self.path_tranHistory = f'{self.path_permData}\\TransactionHistory.csv'
            self.path_accLedger = f'{self.path_permData}\\AccountLedger.csv'
        else:
            print('Working drive not found')
            return

        self.transaction_table = TransactionTable(path=self.path_tranHistory, directory=self.path_artifacts,
                                                  bool_debug=bool_debug)
        self.file_register = FileRegister(path=self.path_dataReg, directory=self.path_artifacts, bool_debug=bool_debug)
        self.account_ledger = AccountLedger(path=self.path_accLedger, directory=self.path_artifacts)

        if bool_debug:
            print(f"Title: {self.title}")
            print(f"Path: {self.path}")
            print(f"Transaction data: {len(self.transaction_table.data.index)} records found")
            print(f"Data Registry: {len(self.file_register.data.index)} files found")

    def register_new_files(self, save=True, reset=False):
        discovered_files = os.listdir(self.path_rawData)
        registered_files = self.file_register.data['File'].values
        if reset:
            df = pd.DataFrame({'File': discovered_files})
            df['Status'] = 'New'
            self.file_register.data = df
        else:
            for new_file in discovered_files:
                if new_file in registered_files:
                    continue
                else:
                    newline = pd.DataFrame({'File': [new_file], 'Status': ['New']})
                    self.file_register.add_data(newline)
        if save:
            self.file_register.save()

    def process_new_files(self, save=True, try_all=False):
        if try_all:
            file_queue = self.file_register.data
        else:
            file_queue = self.file_register.data[self.file_register.data['Status'] == 'New']

        for ind, row in file_queue.iterrows():
            obj = self.extract_data(self.path_rawData + row['File'])

            if obj is not None:
                self.file_register.data.at[ind, 'Status'] = obj.result
                self.file_register.data.at[ind, 'Institution'] = obj.institution
            else:
                self.file_register.data.at[ind, 'Status'] = 'Failed'
                continue

            if obj.result == 'Success':
                if isinstance(obj, CardStatement):
                    if obj.transactions is not None:
                        self.transaction_table.add_data(obj.transactions)
                        self.file_register.data.at[ind, 'Transactions'] = len(obj.transactions)
                    else:
                        self.file_register.data.at[ind, 'Transactions'] = 0

        if save:
            self.save_transactions()
            self.save_dataregistry()
            self.save_accountledger()

    def save_dataregistry(self, name=None):
        if name is None:
            self.file_register.data.to_csv(self.path_dataReg)
        else:
            self.file_register.data.to_csv(f'{self.path_permData}\\{name}.csv')

    def save_transactions(self, name=None):
        if name is None:
            self.transaction_table.data.to_csv(self.path_tranHistory)
        else:
            self.transaction_table.data.to_csv(f'{self.path_permData}\\{name}.csv')

    def save_accountledger(self, name=None):
        if name is None:
            self.account_ledger.data.to_csv(self.path_accLedger)
        else:
            self.account_ledger.data.to_csv(f'{self.path_permData}\\{name}.csv')


class TransactionTable:
    def __init__(self, path=None, directory=None, bool_debug=False):
        cols = ["Date", "Amount", "Account", "Description", "Category"]
        self.path = path
        self.directory = directory
        if path is not None:
            if os.path.exists(path):
                self.data = pd.read_csv(path, index_col=0)
            else:
                self.data = pd.DataFrame(columns=cols)
        else:
            self.data = pd.DataFrame()
        if bool_debug:
            print(self.data.groupby(by='Account').count())

    def add_data(self, new_data):
        if isinstance(new_data, pd.DataFrame):
            self.data = pd.concat([self.data, new_data], ignore_index=True)

    def save(self, path=None):
        if path:
            self.data.to_csv(path)
        elif self.path:
            self.data.to_csv(self.path)
        else:
            print(f'No path provided for Transaction table')


class FileRegister:
    def __init__(self, path=None, directory=None, bool_debug=False):
        cols = ['File', 'Status']
        self.path = path
        self.directory = directory
        if path is not None:
            if os.path.exists(path):
                self.data = pd.read_csv(path, index_col=0)
            else:
                self.data = pd.DataFrame(columns=cols)
        else:
            self.data = pd.DataFrame(columns=cols)

    def add_data(self, new_data):
        if isinstance(new_data, pd.DataFrame):
            self.data = pd.concat([self.data, new_data], ignore_index=True)
        if isinstance(new_data, list):
            new_df = pd.DataFrame(new_data, columns=["File"])
            self.data = pd.concat([self.data, new_df], ignore_index=True)

    def status_display(self):
        print(self.data.groupby(by='Status').count())

    def save(self, path=None):
        if path:
            self.data.to_csv(path)
        elif self.path:
            self.data.to_csv(self.path)
        else:
            print(f'No path provided for File Register')


class AccountLedger:
    def __init__(self, path=None, directory=None):
        self.path = path
        self.directory = directory
        if path is not None:
            if os.path.exists(path):
                self.data = pd.read_csv(path, index_col=0)
            else:
                self.data = pd.DataFrame()
        else:
            self.data = pd.DataFrame()

    def add_data(self, dic):
        if 'Previous Balance' in dic.keys():
            if 'Period Starting' in dic.keys():
                self.data = pd.concat([self.data, pd.DataFrame(
                    {'Date': dic['Period Starting'], dic['Account']: dic['Previous Balance']},
                    index=[0])], ignore_index=True)
        if 'New Balance' in dic.keys():
            if 'Period Ending' in dic.keys():
                self.data = pd.concat([self.data, pd.DataFrame(
                    {'Date': dic['Period Ending'], dic['Account']: dic['New Balance']},
                    index=[0])], ignore_index=True)

    def save(self, path=None):
        if path:
            self.data.to_csv(path)
        elif self.path:
            self.data.to_csv(self.path)
        else:
            print(f'No path provided for File Register')

    def plot(self):
        cpy = self.data.set_index('Date')
        plt.plot(cpy)
        plt.legend()
        plt.show()
