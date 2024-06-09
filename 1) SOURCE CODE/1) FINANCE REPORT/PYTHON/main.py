from FinanceReport import *
from Statements import UnknownStatement, file_types
import PyPDF2
import re
from datetime import datetime
from StringTools import find_available_filename, dic_as_menu
from tabulate import tabulate


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


def regex_fun(txt):
    pattern = re.compile('YMCA')
    s = pattern.findall(txt)
    # print(txt)
    print(s)


if __name__ == '__main__':
    _dir = r'E:\DEBUG'
    lst_files = os.listdir(_dir)
    test_file = f'{_dir}\\{lst_files[1]}'
    print(test_file, lst_files)
    us = UnknownStatement(test_file)
    result = us.determine_statement_type(debug=True)
    print(result)

    # f = FinanceManager()
    # f.add_new_file(test_file)
    # f.analyst.data_coverage()
