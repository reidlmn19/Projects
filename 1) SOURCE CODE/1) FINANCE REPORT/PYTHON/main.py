from FinanceReport import *
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    sample = 'Santander_Bank-Account_2021-04-24.pdf'
    r = FinanceManager(title="Sample Report - 20230620")
    r.analyst.data_coverage()
    # r.update_data(limit=20, _print=True)
    # r.file_manager.file_register = r.file_manager.file_register.reset_index()
    # r.file_manager.save()
