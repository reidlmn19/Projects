from FinanceReport import Report
from tabulate import tabulate
from datetime import *
import os

if __name__ == '__main__':
    r = Report(title="Sample Report - 20230117", bool_debug=False)
    # print(tabulate(r.df_register.data, headers=r.df_register.data.columns))
    name = r.df_register.data.at[2, 'File']
    print(name)

    obj = r.extract_data(f'{r.path_rawData}\\{name}', process=False)
    os.startfile(obj.path)
    obj.get_rawdata()
    obj.get_summary()
    obj.get_transactions(debug=True)
    # print(obj.transactions)

    print(tabulate(obj.transactions, headers=obj.transactions.columns))

    # r.register_new_files()
    # r.process_new_files(debug=True)

    # n = r.df_register.data.at[26, 'File']
    # p = f'{r.path_rawData}\\{n}'
    # p = r'D:\RawData\Quicksilver_Bank-Statement_Feb2023.pdf'
    # s = CapitalOneStatement(p)
    # s.read_data()
    # print(s.summary)
    # print(s.transactions)
