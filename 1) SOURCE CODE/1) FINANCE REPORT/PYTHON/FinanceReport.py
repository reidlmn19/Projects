import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import win32api
from datetime import date
from tabulate import tabulate
from Statements import*
import StringTools

right_now = date.today()


def extract_file_data(path, process=True):
    objs = None
    if os.path.exists(path):
        if 'betterment' in path.lower():
            objs = [BettermentStatement(path, process=process)]
        elif 'santander' in path.lower():
            santander = SantanderStatement(path, process=process)
            objs = [santander.checking, santander.savings]
        elif 'peoples' in path.lower():
            objs = [PeoplesStatement(path, process=process)]
        elif 'quicksilver' in path.lower():
            objs = [CapitalOneStatement(path, account='Quicksilver', process=process)]
        elif 'platinum' in path.lower():
            objs = [CapitalOneStatement(path, account='Platinum', process=process)]
        elif 'nelnet' in path.lower():
            objs = [NelnetStatement(path, process=process)]
        elif 'irobot' in path.lower():
            objs = [IRobotPaycheck(path, process=process)]
        elif 'fidelity' in path.lower():
            objs = [FidelityStatement(path, process=process)]
        elif 'clearmotion' in path.lower():
            objs = [ClearMotionPaycheck(path, process=process)]
    else:
        print(f'Path invalid: {path}')
    return objs


def finddirectory(keyword='FINANCE'):
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    for i in drives:
        d = win32api.GetVolumeInformation(i)
        if keyword.lower() == d[0].lower():
            return i
    return None


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


def df_to_brokenbar(df, account, status):
    tuple_list = []
    try:
        df['Starting Date'] = pd.to_datetime(df['Starting Date'])
        df['Ending Date'] = pd.to_datetime(df['Ending Date'])
        df['Length'] = (df['Ending Date'] - df['Starting Date'])
        status_match = df[df['Status'] == status]
        account_slice = status_match[status_match['Identifier'] == account]
        for ind, row in account_slice.iterrows():
            tuple_list.append((row['Starting Date'], row['Length']))
    except:
        print(f'Failed {account} - {status}')
    return tuple_list


class FinanceManager:
    def __init__(self, title=None, path=None, path_rawdata=None):
        if path is None:
            self.path = finddirectory()
        else:
            self.path = path

        if title is None:
            self.title = f'Finance Report - {right_now}'
        else:
            self.title = title

        if self.path is not None:
            if path_rawdata is None:
                self.path_rawData = r'\\'.join([self.path, 'RawData\\'])
            else:
                self.path_rawData = path_rawdata
            self.path_artifacts = f'{self.path}Artifacts'
            self.path_report = f'{self.path_artifacts}\\{self.title}'

        else:
            print('Working drive not found')
            return

        self.file_manager = FileManager(raw_data_path=self.path_rawData,
                                        file_register_path=f'{self.path_artifacts}\\FileRegister.csv')
        self.data_manager = DataManager(transaction_table_path=f'{self.path_artifacts}\\Transactions.csv')
        self.analyst = Analyst(self.file_manager, self.data_manager, self.path_report)

    def reset(self, file_manager=True, transaction_table=True, save=False):
        if file_manager:
            self.file_manager.register = pd.DataFrame(columns=FileManager.cols)
            if save:
                self.file_manager.save()
        if transaction_table:
            self.data_manager.transaction_table = pd.DataFrame(columns=DataManager.cols)
            if save:
                self.data_manager.save()

    def update_data(self, save=True, limit=None, _print=False):
        self.file_manager.queue_files()
        if limit is None:
            limit = len(self.file_manager.file_queue)
        for file in self.file_manager.file_queue[0:limit]:
            if _print:
                print(file)
            packages = extract_file_data(f'{self.file_manager.raw_data_path}\\{file}')
            for package in packages:
                try:
                    self.data_manager.add_transactions(package)
                    self.file_manager.register_file(package)
                    if _print:
                        print(f'Registered succesfully: {file} {package.account} {package.result}')
                except:
                    self.file_manager.mark_failed(package)
                    if _print:
                        print(f'Failed to register package: {file}')
            if save:
                self.file_manager.save()
                self.data_manager.save()
        self.file_manager.file_queue = []


class FileManager:
    cols = ['File', 'Status', 'Account', 'Institution', 'Starting Date', 'Ending Date']
    file_types = {0: "Peoples Credit Union - Savings",
                  1: "Peoples Credit Union - Checking",
                  2: "Santander - Checking",
                  3: "Santander - Savings",
                  4: "Capital One - Platinum",
                  5: "Capital One - QuickSilver",
                  6: "iRobot - Paycheck",
                  7: "ClearMotion - Paycheck",
                  8: "Nelnet",
                  9: "Betterment",
                  10: "Fidelity"}

    def __init__(self, file_register_path, raw_data_path=None):
        self.raw_data_path = raw_data_path
        self.file_register_path = file_register_path

        if os.path.exists(self.file_register_path):
            self.register = pd.read_csv(self.file_register_path, index_col=0)
        else:
            self.register = pd.DataFrame(columns=FileManager.cols)

        self.raw_data = os.listdir(self.raw_data_path)
        self.file_queue = []

    def queue_files(self, by_status=None):
        if by_status is None:
            by_status = ['New']
        else:
            by_status = by_status
        queue = self.raw_data
        for file in queue:
            file_not_in_list = file not in list(self.register['File'])
            if file_not_in_list:
                continue
            file_matches = pd.DataFrame()
            for status in by_status:
                file_matches = pd.concat([file_matches, self.register[
                    (self.register['File'] == file) & (self.register['Status'] == status)]])
            if file_matches.empty:
                queue = [i for i in queue if i != file]
        self.file_queue = queue

    def mark_failed(self, package):
        name = package.path.split('\\')[-1]
        dic = {
            'File': name,
            'Status': package.result,
            'Account': package.account,
            'Institution': package.institution,
        }
        if name in self.register['File']:
            self.register.loc[self.register['File'] == name] = dic
        else:
            self.register = pd.concat([self.register, pd.DataFrame(dic, index=[0])],
                                      ignore_index=True).drop_duplicates()
        self.save()

    def register_file(self, package):
        name = package.path.split('\\')[-1]
        dic = {
            'File': name,
            'Status': package.result,
            'Account': package.account,
            'Institution': package.institution,
            'Starting Date': package.summary['Starting Date'],
            'Ending Date': package.summary['Ending Date']
        }
        self.register = pd.concat([self.register, pd.DataFrame(dic, index=[0])], ignore_index=True)
        self.register.drop_duplicates(subset=['File', 'Account', 'Institution'], ignore_index=True, inplace=True)
        self.save()

    def save(self, path=None):
        if path:
            self.register.to_csv(path)
        elif self.file_register_path:
            self.register.to_csv(self.file_register_path)
        else:
            print(f'No path provided for File Register')

    def sort_filenames(self, rename=True):
        contents = os.listdir(self.raw_data_path)
        test = f'{self.raw_data_path}\\{contents[0]}'
        print(StringTools.dic_as_menu(FileManager.file_types))
        os.startfile(test)
        s = int(input(f'{contents[0]}'))
        print(f'File {contents[0]} identified as type {FileManager.file_types[s]}')


class DataManager:
    cols = ["Date", "Amount", "Account", "Description", "Category"]

    def __init__(self, transaction_table_path):
        self.transaction_table_path = transaction_table_path
        if os.path.exists(self.transaction_table_path):
            self.transaction_table = pd.read_csv(self.transaction_table_path, index_col=0)
        else:
            self.transaction_table = pd.DataFrame(columns=DataManager.cols)

    def add_transactions(self, package):
        balance = package.transactions['Amount'].cumsum() + package.summary['Starting Balance']
        package.transactions[f'{package.account}_{package.institution}_balance'] = balance
        package.transactions['Source'] = package.path
        package.transactions['Category'] = [categorize(desc) for desc in list(package.transactions['Description'])]
        self.transaction_table = pd.concat([self.transaction_table, package.transactions], ignore_index=True)
        self.transaction_table.drop_duplicates(
            subset=['Date', 'Amount', 'Account', 'Description', 'Institution', 'Source'],
            ignore_index=True, inplace=True)

    def save(self, transaction_table=True):
        if transaction_table:
            self.transaction_table.to_csv(self.transaction_table_path)


class Analyst:
    def __init__(self, file_manager, data_manager, path):
        self._file_manager = file_manager
        self._data_manager = data_manager
        self.path = path
        self.accounts = self.get_accounts()

    def account_balances(self):
        cols = [col for col in self._data_manager.transaction_table.columns if 'balance' in col.lower()]
        x = self._data_manager.transaction_table['Date'].values
        y = self._data_manager.transaction_table[cols].values
        plt.plot(x, y)
        plt.legend(cols)
        plt.show()

    def get_accounts(self):
        self._file_manager.register['Identifier'] = (self._file_manager.register['Account'].map(str) + '_' +
                                                     self._file_manager.register['Institution'].map(str))
        accounts = self._file_manager.register['Identifier'].unique()
        ind_nan = np.argwhere(accounts == 'nan_nan')
        accounts = np.delete(accounts, ind_nan)
        return accounts

    def data_coverage(self, by_status=None, bar_height=5, bar_pad=2.5, color_dic=None, today=True):
        if by_status is None:
            by_status = ['Success']
        else:
            by_status = by_status

        if color_dic is None:
            color_dic = {'Success': '#13850b',
                         'Other': '#e6c63c'}
        else:
            color_dic = color_dic

        fig, ax = plt.subplots()
        y_height = bar_pad
        ticks = []
        labels = []
        for account in self.accounts:
            for status in by_status:
                ax.broken_barh(df_to_brokenbar(self._file_manager.register, account, status),
                               (y_height, bar_height), facecolors=color_dic[status])
            ticks.append(y_height + bar_height / 2)
            labels.append(account)
            y_height = y_height + bar_height + bar_pad
        if today:
            plt.axvline(right_now, color='y', linestyle='--', label='Today')
        ax.grid(True)
        ax.set_yticks(ticks, labels=labels)
        plt.show()

    def file_results(self, colors=None):
        if colors is None:
            colors = {
                'Success': '#13850b',
                'Failed': '#fa3442',
                'No Date': '#3459fa',
                'No Transactions': '#FFFF00'
            }
        else:
            colors = colors

        results = pd.DataFrame()
        statuses = self._file_manager.register['Status'].unique()
        for account in self.accounts:
            by_account = self._file_manager.register[self._file_manager.register['Identifier'] == account]
            total = len(by_account)
            dic = {}
            for status in statuses:
                by_status = by_account[by_account['Status'] == status]
                count = len(by_status)
                percent = count / total
                dic[status] = percent
            new_entry = pd.DataFrame(dic, index=[account])
            results = pd.concat([results, new_entry])

        results.sort_values('Success', inplace=True)
        lefts = np.zeros(len(results.index))
        for result in results:
            if result in colors:
                plt.barh(results.index, results[result], label=result, color=colors[result], left=lefts)
            else:
                plt.barh(results.index, results[result], label=result, left=lefts)
            lefts += results[result].values
        plt.legend(loc='lower center')
        plt.title('Results by account')
        plt.show()
