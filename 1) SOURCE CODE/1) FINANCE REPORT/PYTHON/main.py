from FinanceReport import Report
from StringTools import santander_transaction
from tabulate import tabulate
from datetime import *
import os

if __name__ == '__main__':
    r = Report(title="Sample Report - 20230117", bool_debug=False)
    r.register_new_files()
    print(tabulate(r.df_register.data))
    # name = r.df_register.data.at[9, 'File']

    # obj = r.extract_data(f'{r.path_rawData}\\{name}', process=False)
    # os.startfile(obj.path)
    # obj.get_rawdata()
    # obj.get_summary()
    # obj.get_transactions(debug=True)
    # print(tabulate(obj.transactions, headers=obj.transactions.columns))

