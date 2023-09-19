from datetime import datetime
import pandas as pd


def str_to_date(s, year=None):
    formats = [
        '%b. %d, %Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%m/%d/%Y',
        '%b %d',
        '%m/%d/%y',
        '%m-%d',
        '%d-%b'
    ]
    for f in formats:
        try:
            d = datetime.strptime(s, f)
            if year:
                d = d.replace(year=year)
            return [d]
        except:
            pass
    if len(s) >= 10:
        try:
            split = s.split(' - ')
            d1 = split[0].strip()
            d2 = split[1].strip()
            if '.' in d1:
                d = [datetime.strptime(d1, '%b. %d, %Y'), datetime.strptime(d2, '%b. %d, %Y')]
            else:
                d = [datetime.strptime(d1, '%b %d, %Y'), datetime.strptime(d2, '%b %d, %Y')]
            return d
        except:
            pass
    return None


def str_to_number(s):
    neg = False
    pct = False
    if '$' in s:
        s = s.replace('$', '')
    if ',' in s:
        s = s.replace(',', '')
    if '=' in s:
        s = s.replace('=', '')
    if '%' in s:
        s = s.replace('%', '')
        pct = True
    if '+' in s:
        s = s.replace('+', '')
        pos = True
    elif '-' in s:
        s = s.replace('-', '')
        neg = True
    s.strip()

    try:
        num = float(s)
        if neg:
            num = abs(num) * -1
        if pct:
            num = num / 100
        return num
    except:
        pass


def categorize(s):
    dic = {'Subscriptions': ['Apple', 'Spotify'],
           'Groceries': ['Crosby', 'Market', 'Basket', 'Wegmans', 'Hannaford', 'WHOLEFDS', 'stop & shop',
                         'LENS.COM',
                         'PETSMART', 'SHOP N` GO'],
           'Restaurants': ['Resta', 'Kitchen', 'Grill', 'Bambolina', 'Burger', 'Wendy', 'Blue Lobster', 'Deli',
                           '5Guys',
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

