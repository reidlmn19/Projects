import pandas as pd
import datetime

class PeoplesCreditUnionStatement:

    def __init__(self, path):
        self.path = path
        self.institution = 'PeoplesCredit'
        self.type = 'Statement'

    def read_data(self):
        return self.institution

    def read_transaction_history(self):
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
                period_begin = datetime.datetime.strptime(df_data.index.min(), '%m/%d/%Y')
                list_periodbegin.append(period_begin)

                period_end = datetime.datetime.strptime(df_data.index.max(), '%m/%d/%Y')
                list_periodend.append(period_end)

        df_data = pd.concat(list_data)

        # for i in df_data['Transaction Description'].values:
        #     list_category.append(categorize(i))
        #
        # df_data.set_index(pd.to_datetime(df_data.index))
        # df_data.rename(columns={'Withdrawals': 'Amount'})
        #
        # df_data['Category'] = list_category
        # dic_files = {"Period Begin": list_periodbegin, "Period End": list_periodend, "File Name": list_files,
        #              'Institution': 'Peoples', 'Type': 'Bank'}
        # df_source = pd.DataFrame(dic_files)

        return df_data