from FinanceReport import Report
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    r = Report(title="Sample Report - 20230117", bool_debug=False)
    r.register_new_files()
    name = r.df_register.data.at[0, 'File']
    print(tabulate(r.df_register.data, headers=r.df_register.data.columns))
    print(name)

    obj = r.extract_data(f'{r.path_rawData}\\{name}', process=False)
    obj.get_rawdata()
    obj.get_summary(debug=True)
    print(obj.summary)
    os.startfile(obj.path)

