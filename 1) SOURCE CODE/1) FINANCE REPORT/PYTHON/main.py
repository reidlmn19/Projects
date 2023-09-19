from FinanceReport import FinanceManager
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    r = FinanceManager(title="Sample Report - 20230620", bool_debug=False)

    # f1 = r'D:\\\RawData\Santander_Bank-Account_2021-03-24.pdf'
    # f2 = r'D:\\\RawData\Santander_Bank-Account_2022-08-24.pdf'
    # obj = r.extract_data(f2)

    r.register_new_files(save=True, reset=True)
    r.process_new_files(save=True)
    r.file_register.status_display()

    # _df = r.df_trans.data
    # _df = r.df_register.data

    # print(tabulate(_df[_df['Status']=='Incomplete'], headers=_df.columns))

    # name = 'ClearMotion_Pay-Check_2020-12-24.pdf'
    # obj = r.extract_data(f'{r.path_rawData}\\{name}')
    # print(obj.summary)
    # os.startfile(obj.path)
