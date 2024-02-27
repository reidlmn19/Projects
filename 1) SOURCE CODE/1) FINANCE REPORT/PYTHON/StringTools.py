from datetime import datetime
import os
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


def dic_as_menu(dic):
    s = ''
    for key in dic:
        s = s + f'\n{key}: {dic[key]}'
    return s


def find_available_filename(s):
    base, ext = s.split('.')
    counter = 1
    print(base, ext, counter)
    while os.path.exists(s):
        s = f'{base}({counter}).{ext}'
        counter = counter + 1
    return s
