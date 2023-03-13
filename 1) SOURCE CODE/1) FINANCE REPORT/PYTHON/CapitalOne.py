from tika import parser
import datetime
import pandas as pd
import PyPDF2


def getEntry(key, list):
    for i in list:
        if key in i:
            return i
    return


class CapitalOneStatement:
    def __init__(self, path, account=None):
        self.path = path
        self.institution = 'CapitalOne'
        self.type = 'Statement'
        if account is None:
            self.account = 'Unknown'
        else:
            self.account = account

        self.info = pd.DataFrame()
        self.summary = pd.DataFrame()
        self.transactions = pd.DataFrame()

    def get_summary(self, raw_list):
        dic = {}
        state = 0
        for item in raw_list:
            if item == "Account Summary":
                state = 1
                continue
            elif item in dic.keys():
                state = 1
                continue
            elif item == "Previous Balance":
                if state == 1:
                    state = 2
                continue
            elif state == 2:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Previous Balance"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Other Credits":
                if state == 1:
                    state = 3
                continue
            elif state == 3:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Other Credits"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Transactions":
                if state == 1:
                    state = 4
                continue
            elif state == 4:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Transactions"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Cash Advances":
                if state == 1:
                    state = 5
                continue
            elif state == 5:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Cash Advances"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Fees Charged":
                if state == 1:
                    state = 6
                continue
            elif state == 6:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Fees Charged"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Interest Charged":
                if state == 1:
                    state = 7
                continue
            elif state == 7:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Interest Charged"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "New Balance":
                if state == 1:
                    state = 8
                continue
            elif state == 8:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["New Balance"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item == "Credit Limit":
                if state == 1:
                    state = 9
                continue
            elif state == 9:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Credit Limit"] = amount
                        state = 10
                    except:
                        state = 1
                continue
            elif state == 10:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        dic["Available Credit"] = amount
                        state = 1
                    except:
                        state = 1
                continue
            elif item in ['7490', '5009', '4586']:
                if state == 1:
                    state = 11
                continue
            elif state == 11:
                try:
                    remove_chars = item.replace('.', '')
                    remove_chars = remove_chars.replace(',', '')
                    date = datetime.datetime.strptime(remove_chars, '%b %d %Y')
                    dic["Start Date"] = date
                    state = 12
                except:
                    state = 1
                continue
            elif state == 12:
                if item == ' - ':
                    continue
                try:
                    remove_chars = item.replace('.', '')
                    remove_chars = remove_chars.replace(',', '')
                    date = datetime.datetime.strptime(remove_chars, '%b %d %Y')
                    dic["End Date"] = date
                    state = 1
                except:
                    state = 1
                continue
        self.summary = dic
        if dic["Start Date"].year == dic["End Date"].year:
            self.year = dic["Start Date"].year

    def get_transactions(self, raw_list):
        lst_desc = []
        lst_date = []
        lst_amount = []
        state = 0
        y1 = self.summary["Start Date"].year
        y2 = self.summary["End Date"].year
        for item in raw_list:
            if item.lower() == 'date':
                state = 1
                continue
            elif item.lower() == 'description':
                if state == 1:
                    state = 2
                else:
                    state = 0
                continue
            elif item.lower() == 'amount':
                if state == 2:
                    state = 3
                else:
                    state = 0
                continue
            elif state == 3:
                try:
                    cells = item.split()
                    d = int(cells[1])
                    m = datetime.datetime.strptime(cells[0], '%b')
                    if m.month == 1:
                        y = y2
                    else:
                        y = y1
                    date = datetime.date(y, m.month, d)
                    state = 4
                except:
                    state = 0
                continue
            elif state == 4:
                desc = item
                state = 5
                continue
            elif state == 5:
                if '$' in item.lower():
                    remove_chars = item.replace('$', '')
                    remove_chars = remove_chars.replace(' ', '')
                    remove_chars = remove_chars.replace(',', '')
                    try:
                        amount = float(remove_chars)
                        lst_date.append(date)
                        lst_desc.append(desc)
                        lst_amount.append(amount)
                        state = 3
                    except:
                        desc = desc + item
                else:
                    desc = desc + item
        df = pd.DataFrame({"Date": lst_date,
                           "Description": lst_desc,
                           "Amount": lst_amount,
                           "Account": [self.account] * len(lst_date),
                           "Institution": [self.institution] * len(lst_date)})
        self.transactions = df

    def get_PDFinfo(self):
        reader = PyPDF2.PdfReader(self.path)
        m_data = reader.metadata
        self.info = m_data
        return

    def read_data(self):
        pages_list = []
        reader = PyPDF2.PdfReader(self.path)
        for page in reader.pages:
            page_text = page.extractText()
            page_list = page_text.split('\n')
            pages_list.extend(page_list)
        self.get_PDFinfo()
        self.get_summary(pages_list)
        self.get_transactions(pages_list)


class PlatinumStatement:
    def __init__(self, path):
        self.path = path
        self.institution = 'CapitalOne'
        self.type = 'Statement'
        self.account = 'Quicksilver'

    def read_data(self):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        list_files = []
        list_paydate = []
        list_periodbegin = []
        list_periodend = []
        list_date = []
        list_description = []
        list_category = []
        list_amount = []

        for i in list:
            if 'Platinum' in i:
                file = i
                list_files.append(file)
                print("Active file: " + file)

                p = parser.from_file(file)
                raw = p['content'].split('\n')
                raw[:] = [x for x in raw if x]

                d = getEntry('days in Billing Cycle', raw)
                d = d.replace(',', '').replace('.', '')
                dates = d.split('|')[0].split(' - ')

                start_date = datetime.datetime.strptime(dates[0], '%b %d %Y')
                list_periodbegin.append(start_date)

                end_date = datetime.datetime.strptime(dates[1].strip(' '), '%b %d %Y')
                yr = end_date.year
                list_periodend.append(end_date)

                pay_date = end_date
                list_paydate.append(pay_date)

                j = raw.index('Visit www.capitalone.com to see detailed transactions.') + 6
                e_desc = ''
                e_add = ''
                e_date = ''
                while j < len(raw):
                    if 'Total Transactions for This Period' in raw[j]:
                        break
                    try:
                        c = raw[j].split(' ')
                        for k in c:
                            if k in months:
                                e_date = ' '.join(c[:2])
                            elif '$' in k:
                                e_add = k
                            else:
                                e_desc = e_desc + k + ' '
                    except:
                        if raw[j] in months:
                            e_date = ' '.join(c[:2])
                        elif '$' in raw[j]:
                            e_add = k
                        else:
                            e_desc = e_desc + k + ' '
                    if e_date and e_desc and e_add:
                        e_date = e_date + ' ' + str(yr)
                        e_date.replace(',', '')
                        e_date = datetime.datetime.strptime(e_date, '%b %d %Y')
                        list_date.append(e_date)
                        e_date = ''

                        list_amount.append(round(float(e_add.replace('$', '').replace(',', '')), 2))
                        e_add = ''

                        d = e_desc.split(' ')
                        e_desc = ' '.join(d[1:-1])
                        e_cat = None
                        list_description.append(e_desc)
                        list_category.append(e_cat)
                        e_desc = ''
                        e_cat = ''
                    j = j + 1

        dic_data = {'Date': list_date, 'Amount': list_amount, 'Description': list_description,
                    'Category': list_category}
        dic_files = {"Pay Date": list_paydate, "File Name": list_files, "Period Begin": list_periodbegin,
                     "Period End": list_periodend, 'Institution': 'Platinum', 'Type': 'Credit Card'}

        df_files = pd.DataFrame(dic_files)
        df_data = pd.DataFrame(dic_data)

        return df_files, df_data
