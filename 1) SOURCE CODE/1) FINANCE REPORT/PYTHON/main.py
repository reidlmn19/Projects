from FinanceReport import Report
import datetime
from CapitalOne import CapitalOneStatement
import os

test_file = r'D:\RawData\Quicksilver_Bank-Statement_2021-01-01.pdf'

if __name__ == '__main__':
    f = Report(title="Sample Report - 20230117", bool_debug=False)
    nf = f.read_NewFiles(save=False)
    f.saveTransaction('Test.csv')