from FinanceReport import Report
from datetime import *
from CapitalOne import CapitalOneStatement
import os

if __name__ == '__main__':
    r = Report(title="Sample Report - 20230117", bool_debug=False)
    r.register_new_files()
    r.process_new_files(debug=True)

    # n = r.df_register.data.at[26, 'File']
    # p = f'{r.path_rawData}\\{n}'
    # p = r'D:\RawData\Quicksilver_Bank-Statement_Feb2023.pdf'
    # s = CapitalOneStatement(p)
    # s.read_data()
    # print(s.summary)
    # print(s.transactions)
