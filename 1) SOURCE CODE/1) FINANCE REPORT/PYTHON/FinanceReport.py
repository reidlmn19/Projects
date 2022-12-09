import pdftools
import os
import pandas as pd
import win32api
import plotting
import datetime

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


def findDrive(keyword):
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for i in drives:
        d = win32api.GetVolumeInformation(i)
        if keyword.lower() == d[0].lower():
            return i
    return None


class Report:
    def __init__(self, path=None):
        if path is None:
            self.path = findDrive('finance')
        else:
            self.path = path

        self.path_statements = r'\\'.join([self.path, 'Statements\\'])
        self.path_graphs = r'\\'.join([self.path, 'Graphs\\'])
        self.path_analysis = r'\\'.join([self.path, 'Analysis\\'])
        self.title = f'Financial Report - {right_now}'

        self.debits = None
        self.credits = None
        self.loans = None
        self.savings = None
        self.investments = None

    def add_debit(self, name, df):
        self.debits = {name, df}

    def add_credits(self, name, df):
        self.credits = {name, df}

    def add_loans(self, name, df):
        self.loans = {name, df}

    def add_savings(self, name, df):
        self.savings = {name, df}

    def add_investments(self, name, df):
        self.investments = {name, df}

    def run(self):
        print(f'Main report thread')
        self.load_permanant_data


class BankingAccount:

    def __init__(self, name, list_inputfiles):
        # Input name of institution, read all of the matching source documents, create data frames, then save to excel
        print("\nCreating bank object for " + name)
        self.name = name
        home_dir = findDrive('finance')
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

    def getdata(self, list):  # / Look at source files, create data frame for source files and another for data
        if self.name == 'ClearMotion':
            df1, df2 = pdftools.ClearMotion(list)
            return df1, df2
        elif self.name == 'iRobot':
            df1, df2 = pdftools.iRobot(list)
            return df1, df2
        elif self.name == 'Quicksilver':
            df1, df2 = pdftools.Quicksilver(list)
            return df1, df2
        elif self.name == 'Platinum':
            df1, df2 = pdftools.Platinum(list)
            return df1, df2
        elif self.name == 'Santander':
            df1, df2 = pdftools.Santander(list)
            return df1, df2
        elif self.name == 'Peoples':
            df1, df2 = pdftools.Peoples(list)
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


class TransactionHistory(pd.DataFrame):
    def __init__(self, path=None, data=None, index=None, columns=None):
        super().__init__(self, data, index, columns)
        if os.path.exists(self.path_statements):
            self.drivefound = True
        for i in self.institutions:
            print(i)

    def add_data(self, data):
        if isinstance(data, pd.DataFrame):
            pd.Dataframe.merge(data)


class DataRegistry(pd.DataFrame):
    def __init__(self, path=None, data=None, index=None, columns=None):
        super().__init__(self, data, index, columns)
        if os.path.exists(self.path_statements):
            self.drivefound = True
        for i in self.institutions:
            print(i)

    def add_data(self, data):
        if isinstance(data, pd.DataFrame):
            pd.Dataframe.merge(data)


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
