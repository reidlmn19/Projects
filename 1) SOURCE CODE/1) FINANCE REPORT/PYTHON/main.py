from FinanceReport import *
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    sample = 'Santander_Bank-Account_2021-04-24.pdf'
    test_data = r'D:\OCT2023DATA'
    r = FinanceManager(title="Sample Report - 20230620", path_rawdata=test_data)
    f = f'{r.path_rawData}\\{r.file_manager.raw_data[0]}'
    print(f)

    # r.update_data(_print=True)
    # r.analyst.data_coverage()
    # r.analyst.file_results()
