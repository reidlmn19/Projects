from FinanceReport import *
from tabulate import tabulate
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import PyPDF2
import os


def get_pdf_author(path, show_all=False):
    print(path)
    matches = {
        'Nelnet': NelnetStatement,
        'Betterment': BettermentStatement
    }
    reader = PyPDF2.PdfReader(path)
    author = reader.metadata.author
    if author in matches:
        return matches[author]

    pages_text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        pages_text = pages_text + page_text
    print(pages_text)



if __name__ == '__main__':
    sample = 'Santander_Bank-Account_2021-04-24.pdf'
    test_data = r'E:\OCT2023DATA'
    r = FinanceManager(title="Sample Report - 20230620", path_rawdata=test_data)

    target = r'E:\OCT2023DATA\Betterment_401k_Quarterly_Statement_2023-09-30.pdf'
    obj = get_pdf_author(target, show_all=True)
    print(obj)

    # for file in r.file_manager.raw_data:
    #     f = f'{r.path_rawData}\\{file}'
    #     get_file_author(f)
