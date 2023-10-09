from FinanceReport import *
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    sample = 'Santander_Bank-Account_2021-04-24.pdf'
    r = FinanceManager(title="Sample Report - 20230620")
    r.update_data(limit=1, _print=True)
    r.analyst.data_coverage()
