import pdftools
import os
import pandas as pd
import win32api
import datetime

from Betterment import *
from Santander import *
from PeoplesCreditUnion import *
from CapitalOne import *
from Nelnet import *
from iRobot import *
from Fidelity import *

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


def findDirectory(keyword='FINANCE'):
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
            self.path = findDirectory()
        else:
            self.path = path

        if title is None:
            self.title = f'Finance Report - {datetime.date.today()}'
        else:
            self.title = title

        if self.path is not None:
            self.path_rawData = r'\\'.join([self.path, 'RawData\\'])

            self.path_artifacts = r'\\'.join([self.path, 'Artifacts\\'])
            self.path_Report = f'{self.path_artifacts}\\{self.title}'

            self.path_permData = r'\\'.join([self.path, 'PermanentData\\'])
            self.path_dataReg = f'{self.path_permData}\\DataRegistry.csv'
            self.path_tranHistory = f'{self.path_permData}\\TransactionHistory.csv'

        self.df_trans = TransactionHistory(path=self.path_tranHistory, bool_debug=bool_debug)
        self.df_register = DataRegistry(path=self.path_dataReg, bool_debug=bool_debug)

        if bool_debug:
            print(f"Title: {self.title}")
            print(f"Path: {self.path}")
            print(f"Transaction data: {len(self.df_trans.data.index)} records found")
            print(f"Data Registry: {len(self.df_register.data.index)} files found")

    def extract_data(self, path):
        dat = None
        if os.path.exists(path):
            if 'betterment' in path.lower():
                # f = BettermentStatement(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'santander' in path.lower():
                # f = SantanderStatement(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'peoples' in path.lower():
                # f = PeoplesCreditUnionStatement(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'quicksilver' in path.lower():
                f = CapitalOneStatement(path, account='Quicksilver')
                f.read_data()
                dat = f.transactions
            elif 'platinum' in path.lower():
                f = CapitalOneStatement(path, account='Platinum')
                f.read_data()
                dat = f.transactions
            elif 'nelnet' in path.lower():
                # f = NelnetStatement(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'irobot' in path.lower():
                # f = iRobotPaycheck(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'fidelity' in path.lower():
                # f = FidelityStatement(path)
                print(f'Not yet supported {path}')
                f = None
            elif 'clearmotion' in path.lower():
                # f = FidelityStatement(path)
                print(f'Not yet supported {path}')
                f = None
            else:
                print(f'File not recognized: {path}')
                f = None
        else:
            print(f'Path invalid: {path}')
        return dat

    def register_NewFiles(self, save=False):
        discovered_files = os.listdir(self.path_rawData)
        registered_files = self.df_register.data['File'].values
        for new_file in discovered_files:
            if new_file in registered_files:
                continue
            else:
                newline = pd.DataFrame({'File': [new_file], 'Status': ['New']})
                self.df_register.add_data(newline)
        if save:
            self.saveDataRegistry()

    def read_NewFiles(self, save=False, debug=False, isolate=None):
        file_queue = self.df_register.data[self.df_register.data['Status'] == 'New']
        for ind, row in file_queue.iterrows():
            print(row['File'])
            f = self.path_rawData + row['File']
            trans = self.extract_data(f)
            if debug:
                print(row['File'])
                print(trans)
                s = input('look good? y/n')
                if s == 'y':
                    self.df_register.data.at[ind, 'Status'] = 'Done'
                    self.df_trans.add_data(trans)
                else:
                    self.df_register.data.at[ind, 'Status'] = 'Fail'
            else:
                self.df_register.data.at[ind, 'Status'] = 'Done'
                self.df_trans.add_data(trans)
        if save:
            self.saveTransaction('Test2.csv')

    def saveDataRegistry(self, path=None):
        if path is None:
            self.df_register.data.to_csv(f'{self.path_permData}\\DataRegistry.csv')
        else:
            self.df_register.data.to_csv(path)

    def saveTransaction(self, name='TransactionHistory.csv'):
        self.df_trans.data.to_csv(f'{self.path_permData}\\{name}')



class BankingAccount:

    def __init__(self, name, list_inputfiles):
        # Input name of institution, read all of the matching source documents, create data frames, then save to excel
        print("\nCreating bank object for " + name)
        self.name = name
        home_dir = findDirectory()
        name_scfile = r'\\'.join([home_dir, "Statements", self.name + '_df_sourcefile.csv'])
        name_datfile = r'\\'.join([home_dir, "Statements", self.name + '_dat_sourcefile.csv'])
        for j in list_inputfiles:
            if self.name in j:
                print('Sourcefiles for ', self.name, ' found')
                print('Opening: ', name_scfile)
                self.df_sourcefiles = pd.read_csv(name_scfile)
                print('Opening: ', name_datfile)
                self.df_data = pd.read_csv(name_datfile)
                return
        print('Sourcefile not found, gathering data')
        self.df_sourcefiles, self.df_data = self.getdata(list)
        print("Saving source files to: ", name_scfile)
        self.df_sourcefiles.to_csv(name_scfile)
        print("Saving data to: ", name_datfile)
        self.df_data.to_csv(name_datfile)
        print('Paycheck not in reference table')

    def getdata(self, lst):  # / Look at source files, create data frame for source files and another for data
        if self.name == 'ClearMotion':
            df1, df2 = pdftools.ClearMotion(lst)
            return df1, df2
        elif self.name == 'iRobot':
            df1, df2 = pdftools.iRobot(lst)
            return df1, df2
        elif self.name == 'Quicksilver':
            df1, df2 = pdftools.Quicksilver(lst)
            return df1, df2
        elif self.name == 'Platinum':
            df1, df2 = pdftools.Platinum(lst)
            return df1, df2
        elif self.name == 'Santander':
            df1, df2 = pdftools.Santander(lst)
            return df1, df2
        elif self.name == 'Peoples':
            df1, df2 = pdftools.Peoples(lst)
            return df1, df2
        else:
            print("File not supported")
            return


class CreditAccount:

    def __init__(self, name):
        print(f'Credit account: {name}')


class Loan:

    def __init__(self, name):
        print(f'Loan: {name}')


class InvestmentAccount:

    def __init__(self, name):
        print(f'Investment Account: {name}')


class Employer:

    def __init__(self, name):
        print(f'Investment Account: {name}')


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

# Quicksilver = Institution('Quicksilver', list_input_files)
# Platinum = Institution('Platinum', list_input_files)
# Santander = Institution('Santander', list_input_files)
# Peoples = Institution('Peoples', list_input_files)
# ClearMotion = Institution('ClearMotion', list_input_files)
# iRobot = Institution('iRobot', list_input_files)
# print('\n')

# Define time period to analyze

# period_begin = datetime.datetime(year=2020, month=1, day=1)
# period_end = datetime.datetime(year=2020, month=3, day=1)

# Aggregate source files

# all_inp_files = pd.concat([Quicksilver.df_sourcefiles,
#                            Platinum.df_sourcefiles,
#                            # Santander.df_sourcefiles,
#                            Peoples.df_sourcefiles,
#                            ClearMotion.df_sourcefiles,
#                            iRobot.df_sourcefiles], ignore_index=True)

# pltfunctions.available_data(all_inp_files, period_begin, period_end)

# Aggregate data

# all_transactions = pd.concat([Quicksilver.df_data,
#                               Platinum.df_data,
#                               Peoples.df_data], ignore_index=True)
# Peoples.df_data,
# Santander.df_data], ignore_index=True)

# all_paychecks = pd.concat([ClearMotion.df_data,
#                            iRobot.df_data], ignore_index=True)

# print(all_transactions)
