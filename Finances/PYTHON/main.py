import inpfiles
import os
import pandas as pd
import pltfunctions
import datetime


def df_filter_time(df, start, end):
    for i in df.columns:
        if i in ['Date', 'Pay Date']:
            col = i
    after_start = df[col] >= start
    before_end = df[col] < end
    period = after_start & before_end
    return df[period]


class Institution:

    def __init__(self, name,
                 list):  # Input name of institution, read all of the matching source documents, create data frames, then save to excel
        print("\nCreating object for " + name)
        for i in list_Institutions:
            if i in name:
                print('Institution in reference table')
                self.name = i
                name_scfile = dir_output + self.name + '_df_sourcefile.csv'
                name_datfile = dir_output + self.name + '_dat_sourcefile.csv'
                for j in os.listdir(dir_output):
                    if self.name in j:
                        print('Sourcefiles for ', self.name, ' found')
                        print('Opening: ', name_scfile)
                        self.df_sourcefiles = pd.read_csv(name_scfile)
                        print('Opening: ', name_datfile)
                        self.df_data = pd.read_csv(name_datfile)
                        return
                print('Sourcefile not found, gathering data')
                self.df_sourcefiles, self.df_data = self.getdata(list)
                print("Saving source files to: ", name_scfile)
                self.df_sourcefiles.to_csv(name_scfile)
                print("Saving data to: ", name_datfile)
                self.df_data.to_csv(name_datfile)
        print('Paycheck not in reference table')

    def getdata(self, list):  # / Look at source files, create data frame for source files and another for data
        if self.name == 'ClearMotion':
            df1, df2 = inpfiles.ClearMotion(list)
            return df1, df2
        elif self.name == 'iRobot':
            df1, df2 = inpfiles.iRobot(list)
            return df1, df2
        elif self.name == 'Quicksilver':
            df1, df2 = inpfiles.Quicksilver(list)
            return df1, df2
        elif self.name == 'Platinum':
            df1, df2 = inpfiles.Platinum(list)
            return df1, df2
        elif self.name == 'Santander':
            df1, df2 = inpfiles.Santander(list)
            return df1, df2
        elif self.name == 'Peoples':
            df1, df2 = inpfiles.Peoples(list)
            return df1, df2
        else:
            print("File not supported")
            return


# Debug


# Main Program---------------------------------------------

# List of source files

dir_input = r'D:/'
dir_output = r"C:/Users/relleman/OneDrive/PROJECTS/Finances/OUTPUT_FILES/"

list_Institutions = ['Santander', 'Peoples', 'Quicksilver', 'Platinum', 'ClearMotion',
                     'iRobot', 'Betterment', 'Nelnet']
list_input_files = []
# for i in os.listdir(dir_input):
#     list_input_files.append(dir_input+i)

# Initialize the data

Quicksilver = Institution('Quicksilver', list_input_files)
Platinum = Institution('Platinum', list_input_files)
# Santander = Institution('Santander', list_input_files)
Peoples = Institution('Peoples', list_input_files)
ClearMotion = Institution('ClearMotion', list_input_files)
iRobot = Institution('iRobot', list_input_files)
print('\n')

# Define time period to analyze

period_begin = datetime.datetime(year=2020, month=1, day=1)
period_end = datetime.datetime(year=2020, month=3, day=1)

# Aggregate source files

all_inp_files = pd.concat([Quicksilver.df_sourcefiles,
                           Platinum.df_sourcefiles,
                           # Santander.df_sourcefiles,
                           Peoples.df_sourcefiles,
                           ClearMotion.df_sourcefiles,
                           iRobot.df_sourcefiles], ignore_index=True)

# pltfunctions.available_data(all_inp_files, period_begin, period_end)

# Aggregate data

all_transactions = pd.concat([Quicksilver.df_data,
                              Platinum.df_data,
                              Peoples.df_data], ignore_index=True)
# Peoples.df_data,
# Santander.df_data], ignore_index=True)

all_paychecks = pd.concat([ClearMotion.df_data,
                           iRobot.df_data], ignore_index=True)

print(all_transactions)
