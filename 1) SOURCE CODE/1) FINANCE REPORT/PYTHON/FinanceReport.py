import matplotlib.pyplot as plt
import pandas as pd
import os
import win32api
import datetime

from CardStatements import CapitalOneStatement, SantanderStatement, PeoplesStatement
from InvestmentStatements import FidelityStatement, BettermentStatement
from LoanStatements import NelnetStatement
from Paychecks import IRobotPaycheck, ClearMotionPaycheck

right_now = datetime.date.today()


def categorize(s):
    dic = {'Subscriptions': ['Apple', 'Spotify'],
           'Groceries': ['Crosby', 'Market', 'Basket', 'Wegmans', 'Hannaford', 'WHOLEFDS', 'stop & shop',
                         'LENS.COM',
                         'PETSMART', 'SHOP N` GO'],
           'Restaurants': ['Resta', 'Kitchen', 'Grill', 'Bambolina', 'Burger', 'Wendy', 'Blue Lobster', 'Deli',
                           '5Guys',
                           'PASQUALES', 'CHRISTINAS', 'A1JAPANESEHOUSEROCHESTERNH', 'OPUS', 'Italian', 'Lobsta',
                           'PIZZA', 'Mcdonald', 'Flatbread', 'Wingstop', 'CK PEARL', 'SETTLER'],
           'Alcohol': ['Night Shift', 'Playoffs', 'DNCSS TD GARDEN CONCESBOSTONMA', 'LIQUOR', 'BREWING', 'SHY BIRD',
                       'DEST: SEA'],
           'Travel': ['Jetblue', 'Uber', 'NEWPORT', 'MATTERHORN', 'u-haul', 'KINGSTONRI', 'Vietnam', 'Cruiseport',
                      'NH State Pa'],
           'Ski': ['IKON', 'Killington', 'TICKETSATWORK', 'SMUGGLERS', 'WaitsfieldVT', 'TREMBLA', 'Loon'],
           'Car': ['ARTISAN WEST GARASOMERVILLEMA', 'EXXONMOBIL', 'SUNOCO', 'Shell', 'cumberland', '7-eleven',
                   'A.L. PRIME', 'AL PRIME', 'AUTO', 'RMV', 'E-ZPass', 'Gulf', 'CIRCLE K', 'DCR'],
           'Stores': ['Best Buy', 'Target', 'BestBuy', 'Kohl', 'Dick', 'REI', 'Walmart', 'NORDSTROM', 'Guitar',
                      'Savers', 'Depot', 'LOGITECH', 'DIGI KEY', 'CRAIGSLIST', 'HOMEGOODS', 'HALLOWEE'],
           'Amazon': ['Amazon', 'AMZN'],
           'Gaming': ['STEAMGAMES', 'BLIZZARD', 'Microsoft', 'Nintendo'],
           'Golf': ['GOLF', 'Owl'],
           'Gifts': ['URI', 'HYDROFLASK', 'SOUFEEL'],
           'Charges': ['Adjustment', 'PYMTAuthDate', 'Capital One'],
           'Living': ['Fully', 'COMCAST', 'Pet', 'Animal'],
           'Venmo': ['Venmo'],
           'Income': ['Payroll', 'Acorns', 'IRS treas']
           }
    for i in dic:
        for j in dic[i]:
            if j.lower() in s.lower():
                return i
    return 'Unknown'


def df_filter_time(df, start, end):
    for i in df.columns:
        if i in ['Date', 'Pay Date']:
            col = i
            after_start = df[col] >= start
            before_end = df[col] < end
            period = after_start & before_end
            return df[period]


def finddirectory(keyword='FINANCE'):
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for i in drives:
        d = win32api.GetVolumeInformation(i)
        if keyword.lower() == d[0].lower():
            return i
    return None


class Report:
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

        self.df_trans = TransactionHistory(path=self.path_tranHistory, bool_debug=bool_debug)
        self.df_register = DataRegistry(path=self.path_dataReg, bool_debug=bool_debug)
        self.df_ledger = AccountLedger(path=self.path_accLedger)

        if bool_debug:
            print(f"Title: {self.title}")
            print(f"Path: {self.path}")
            print(f"Transaction data: {len(self.df_trans.data.index)} records found")
            print(f"Data Registry: {len(self.df_register.data.index)} files found")

    def extract_data(self, path, process=True):
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

    def register_new_files(self, save=True):
        discovered_files = os.listdir(self.path_rawData)
        registered_files = self.df_register.data['File'].values
        for new_file in discovered_files:
            if new_file in registered_files:
                continue
            else:
                newline = pd.DataFrame({'File': [new_file], 'Status': ['New']})
                self.df_register.add_data(newline)
        if save:
            self.save_dataregistry()

    def process_new_files(self, save=True, debug=False):
        df_file_summary = pd.DataFrame()
        file_queue = self.df_register.data[self.df_register.data['Status'] == 'New']
        for ind, row in file_queue.iterrows():
            f = self.path_rawData + row['File']
            print(f)
            dat, dic = self.extract_data(f)
            try:
                self.df_trans.add_data(dat)
                self.df_ledger.add_data(dic)
                self.df_register.data.at[ind, 'Status'] = 'Done'
            except:
                self.df_register.data.at[ind, 'Status'] = 'Fail'
            if debug:
                df_file_summary = pd.concat([df_file_summary, pd.DataFrame(dic, index=[row['File']])])
        if save:
            self.save_transactions()
            self.save_dataregistry()
            self.save_accountledger()
            if debug:
                df_file_summary.to_csv(f'{self.path_artifacts}\\FileSummary.csv')

    def save_dataregistry(self, name=None):
        if name is None:
            self.df_register.data.to_csv(self.path_dataReg)
        else:
            self.df_register.data.to_csv(f'{self.path_permData}\\{name}.csv')

    def save_transactions(self, name=None):
        if name is None:
            self.df_trans.data.to_csv(self.path_tranHistory)
        else:
            self.df_trans.data.to_csv(f'{self.path_permData}\\{name}.csv')

    def save_accountledger(self, name=None):
        if name is None:
            self.df_ledger.data.to_csv(self.path_accLedger)
        else:
            self.df_ledger.data.to_csv(f'{self.path_permData}\\{name}.csv')


class TransactionHistory:
    def __init__(self, path=None, bool_debug=False):
        cols = ["Date", "Amount", "Account", "Description", "Category"]
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


class DataRegistry:
    def __init__(self, path=None, bool_debug=False):
        cols = ['File', 'Status']
        if path is not None:
            if os.path.exists(path):
                self.data = pd.read_csv(path, index_col=0)
            else:
                self.data = pd.DataFrame(columns=cols)
        else:
            self.data = pd.DataFrame(columns=cols)

        if bool_debug:
            print(self.data.groupby(by='Status').count())

    def add_data(self, new_data):
        if isinstance(new_data, pd.DataFrame):
            self.data = pd.concat([self.data, new_data], ignore_index=True)
        if isinstance(new_data, list):
            new_df = pd.DataFrame(new_data, columns=["File"])
            self.data = pd.concat([self.data, new_df], ignore_index=True)


class AccountLedger:
    def __init__(self, path=None):
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

    def plot(self):
        cpy = self.data.set_index('Date')
        plt.plot(cpy)
        plt.legend()
        plt.show()
