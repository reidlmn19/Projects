import datetime
import pandas as pd
from tika import parser  # pip install tika


def getEntry(key, list):
    for i in list:
        if key in i:
            return i
    return


def categorize(s):
    dic = {'Subscriptions': ['Apple', 'Spotify'],
           'Groceries': ['Crosby', 'Market', 'Basket', 'Wegmans', 'Hannaford', 'WHOLEFDS', 'stop & shop', 'LENS.COM',
                         'PETSMART', 'SHOP N` GO'],
           'Restaurants': ['Resta', 'Kitchen', 'Grill', 'Bambolina', 'Burger', 'Wendy', 'Blue Lobster', 'Deli', '5Guys',
                           'PASQUALES', 'CHRISTINAS', 'A1JAPANESEHOUSEROCHESTERNH', 'OPUS', 'Italian', 'Lobsta',
                           'PIZZA', 'Mcdonald', 'Flatbread', 'Wingstop', 'CK PEARL', 'SETTLER'],
           'Alcohol': ['Night Shift', 'Playoffs', 'DNCSS TD GARDEN CONCESBOSTONMA', 'LIQUOR', 'BREWING', 'SHY BIRD',
                       'DEST: SEA'],
           'Travel': ['Jetblue', 'Uber', 'NEWPORT', 'MATTERHORN', 'u-haul', 'KINGSTONRI', 'Vietnam', 'Cruiseport',
                      'NH State Pa'],
           'Ski': ['IKON', 'Killington', 'TICKETSATWORK', 'SMUGGLERS', 'WaitsfieldVT', 'TREMBLA', 'Loon'],
           'Car': ['ARTISAN WEST GARASOMERVILLEMA', 'EXXONMOBIL', 'SUNOCO', 'Shell', 'cumberland', '7-eleven',
                   'A.L. PRIME', 'AL PRIME', 'AUTO', 'RMV', 'E-ZPass', 'Gulf', 'CIRCLE K', 'DCR'],
           'Stores': ['Best Buy', 'Target', 'BestBuy', 'Kohl', 'Dick', 'REI', 'Walmart', 'NORDSTROM', 'Guitar',
                      'Savers', 'Depot', 'LOGITECH', 'DIGI KEY', 'CRAIGSLIST', 'HOMEGOODS', 'HALLOWEE'],
           'Amazon': ['Amazon', 'AMZN'],
           'Gaming': ['STEAMGAMES', 'BLIZZARD', 'Microsoft', 'Nintendo'],
           'Golf': ['GOLF', 'Owl'],
           'Gifts': ['URI', 'HYDROFLASK', 'SOUFEEL'],
           'Charges': ['Adjustment', 'PYMTAuthDate', 'Capital One'],
           'Living': ['Fully', 'COMCAST', 'Pet', 'Animal'],
           'Venmo': ['Venmo'],
           'Income': ['Payroll', 'Acorns', 'IRS treas']
           }
    for i in dic:
        for j in dic[i]:
            if j.lower() in s.lower():
                return i
    return 'Unknown'


def Quicksilver(list):
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
        if 'Quicksilver' in i:
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
                    e_cat = categorize(e_desc)
                    list_description.append(e_desc)
                    list_category.append(e_cat)
                    e_desc = ''
                    e_cat = ''
                j = j + 1

    dic_data = {'Date': list_date, 'Amount': list_amount, 'Description': list_description, 'Category': list_category}
    dic_files = {"Pay Date": list_paydate, "File Name": list_files, "Period Begin": list_periodbegin,
                 "Period End": list_periodend, 'Institution': 'Quicksilver', 'Type': 'Credit Card'}

    df_files = pd.DataFrame(dic_files)
    df_data = pd.DataFrame(dic_data)

    return df_files, df_data


def Platinum(list):
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
                    e_cat = categorize(e_desc)
                    list_description.append(e_desc)
                    list_category.append(e_cat)
                    e_desc = ''
                    e_cat = ''
                j = j + 1

    dic_data = {'Date': list_date, 'Amount': list_amount, 'Description': list_description, 'Category': list_category}
    dic_files = {"Pay Date": list_paydate, "File Name": list_files, "Period Begin": list_periodbegin,
                 "Period End": list_periodend, 'Institution': 'Platinum', 'Type': 'Credit Card'}

    df_files = pd.DataFrame(dic_files)
    df_data = pd.DataFrame(dic_data)

    return df_files, df_data


def Santander(list):
    list_files = []
    list_paydate = []
    list_periodbegin = []
    list_periodend = []
    list_date = []
    list_description = []
    list_category = []
    list_amount = []
    list_balance = []

    for i in list:
        if 'Santander' in i:
            file = i
            list_files.append(file)
            print("Active file: " + file)

            p = parser.from_file(file)
            raw = p['content'].split('\n')

            dates = getEntry('Statement Period', raw).split(' ')

            start_date = datetime.datetime.strptime(dates[2], '%m/%d/%y')
            list_periodbegin.append(start_date)

            end_date = datetime.datetime.strptime(dates[4], '%m/%d/%y')
            list_periodend.append(end_date)

            pay_date = end_date
            yr = end_date.year
            list_paydate.append(pay_date)

            j = raw.index('Date Description Additions Subtractions Balance') + 3
            while True:
                if 'Ending Balance' in raw[j]:
                    break
                try:
                    c = raw[j].split(' ')
                    if '-' in c[0]:
                        e_date = datetime.datetime.strptime(c[0], '%m-%d')
                        e_date = e_date.replace(year=yr)
                        list_date.append(e_date)

                        e_add = float(c[-2].replace('$', ' '))
                        list_amount.append(e_add)

                        e_bal = float(c[-1].replace('$', ' '))
                        list_balance.append(e_bal)

                        e_desc = c[1:-3]
                        e_desc = ' '.join(e_desc)
                        e_cat = categorize(e_desc)
                        list_description.append(e_desc)
                        list_category.append(e_cat)
                        j = j + 1
                    else:
                        j = j + 1
                except:
                    j = j + 1

    dic_data = {'Date': list_date, 'Amount': list_amount, 'Description': list_description, 'Balance': list_balance,
                'Category': list_category}
    dic_files = {"Pay Date": list_paydate, "File Name": list_files, "Period Begin": list_periodbegin,
                 "Period End": list_periodend, 'Institution': 'Santander', 'Type': 'Bank'}

    df_files = pd.DataFrame(dic_files)
    df_data = pd.DataFrame(dic_data)

    return df_files, df_data


def Peoples(list):
    list_files = []
    list_periodbegin = []
    list_periodend = []
    list_data = []
    list_category = []

    for i in list:
        if 'Peoples' in i:
            file = i
            list_files.append(file)
            print("Active file: " + file)

            df_data = pd.read_csv(file, index_col=0)
            df_data = df_data.loc[:, ~df_data.columns.str.contains('^Unnamed')]
            list_data.append(df_data)
            df_data = df_data.set_index('Date')
            print(df_data.head(10))
            print(df_data.columns)


            print(df_data.index.min())
            period_begin = datetime.datetime.strptime(df_data.index.min(),'%m/%d/%Y')
            list_periodbegin.append(period_begin)

            period_end = datetime.datetime.strptime(df_data.index.max(),'%m/%d/%Y')
            list_periodend.append(period_end)

    df_data = pd.concat(list_data)

    for i in df_data['Transaction Description'].values:
        list_category.append(categorize(i))

    df_data.set_index(pd.to_datetime(df_data.index))
    df_data.rename(columns={'Withdrawals': 'Amount'})

    df_data['Category'] = list_category
    dic_files = {"Period Begin": list_periodbegin, "Period End": list_periodend, "File Name": list_files,
                 'Institution': 'Peoples', 'Type': 'Bank'}
    df_source = pd.DataFrame(dic_files)

    return df_source, df_data


def ClearMotion(list):
    list_files = []
    list_paydate = []
    list_grosspay = []
    list_netpay = []
    list_periodbegin = []
    list_periodend = []

    for i in list:
        if 'ClearMotion' in i:
            file = i
            list_files.append(file)
            print("Active file: " + file)

            p = parser.from_file(file)
            raw = p['content'].split('\n')

            for j in raw:
                if 'Earnings' in j:
                    gross_pay = j.split(" ")
                    gross_pay = float(gross_pay[2].replace("$", "").replace(",", ""))
                    list_grosspay.append(gross_pay)
                elif 'Net Pay' in j:
                    net_pay = j.split(' $')
                    net_pay = float(net_pay[1].replace(" ", "").replace(",", ""))
                    list_netpay.append(net_pay)
                elif 'Pay Period' in j:
                    dates = j.split(': ')[1]
                    period_begin, period_end = dates.split(' - ')
                    period_begin = datetime.datetime.strptime(period_begin, '%m/%d/%Y')
                    period_end = datetime.datetime.strptime(period_end, '%m/%d/%Y')
                    list_periodbegin.append(period_begin)
                    list_periodend.append(period_end)
                elif 'Pay Date' in j:
                    pay_date = j.split(': ')[1]
                    pay_date = datetime.datetime.strptime(pay_date, '%m/%d/%Y')
                    list_paydate.append(pay_date)

    dic_data = {"Pay Date": list_paydate, "Period Begin": list_periodbegin, "Period End": list_periodend,
                "Gross Pay": list_grosspay, "Net Pay": list_netpay}
    dic_files = {"Pay Date": list_paydate, "Period Begin": list_periodbegin, "Period End": list_periodend, "File Name": list_files,
                 'Institution': 'ClearMotion', 'Type': 'Employer'}

    df_source = pd.DataFrame(dic_files)
    df_data = pd.DataFrame(dic_data)

    return df_source, df_data


def iRobot(list):
    list_files = []
    list_paydate = []
    list_grosspay = []
    list_netpay = []
    list_periodbegin = []
    list_periodend = []

    for i in list:
        if 'iRobot' in i:
            file = i
            list_files.append(file)
            print("Active file: " + file)

            p = parser.from_file(file)
            raw = p['content'].split('\n')

            dict_data = {}

            try:
                net_pay = raw[raw.index('23 GREEN STREET') + 2]
                net_pay = net_pay.replace('$', '').split(" ")
                net_pay = float(net_pay[-1]) / 100 + float(''.join(net_pay[0:-1]))
            except:
                net_pay = 0

            list_netpay.append(net_pay)

            for j in raw:
                if 'Gross Pay' in j:
                    gross_pay = j.split("$")[1].split(" ")
                    gross_pay = float(gross_pay[-1]) / 100 + float(''.join(gross_pay[0:-1]))
                    list_grosspay.append(gross_pay)
                elif 'Period Begin' in j:
                    period_begin = j.split(': ')[1]
                    period_begin = datetime.datetime.strptime(period_begin, '%m/%d/%Y')
                    list_periodbegin.append(period_begin)
                elif 'Period End' in j:
                    period_end = j.split(': ')[1]
                    period_end = datetime.datetime.strptime(period_end, '%m/%d/%Y')
                    list_periodend.append(period_end)
                elif 'Pay Date' in j:
                    pay_date = raw[64].split(': ')[1]
                    pay_date = datetime.datetime.strptime(pay_date, '%m/%d/%Y')
                    list_paydate.append(pay_date)

    dic_data = {"Pay Date": list_paydate, "Period Begin": list_periodbegin, "Period End": list_periodend,
                "Gross Pay": list_grosspay, "Net Pay": list_netpay}
    dic_files = {"Pay Date": list_paydate, "Period Begin": list_periodbegin, "Period End": list_periodend, "File Name": list_files,
                 'Institution': 'ClearMotion', 'Type': 'Employer'}

    df_source = pd.DataFrame(dic_files)
    df_data = pd.DataFrame(dic_data)

    return df_source, df_data
