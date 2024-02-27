from FinanceReport import *
from Statements import UnknownStatement, file_types
import PyPDF2
from datetime import datetime
from StringTools import find_available_filename, dic_as_menu


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
    print(dic_as_menu(file_types))
    test_directory = r'D:\OCT2023DATA'
    test_list = os.listdir(test_directory)
    for test_file in test_list:
        us = UnknownStatement(f'{test_directory}\\{test_file}')
        s = us.determine_statement_type(manual_mode=False)
        print(test_file, s)

    # r = FinanceManager(title=f'Sample Report - {datetime.today()}')
