import numpy as np
import matplotlib.pyplot as plt


def inst_color(inst):
    dic = {'iRobot': [0.392, 0.655, 0.043],
           'ClearMotion': [0.161, 0.655, 0.839],
           'Peoples': [0, 0.525, 0.325],
           'Santander': [0.93, 0, 0],
           'Quicksilver': [0.6, 0.75, 1],
           'Platinum': [0.75, 0.75, 0.75]}
    return dic[inst]
    

def available_data(df, d_start, d_end):
    fig, ax = plt.subplots()
    df = df[['Institution', 'Period Begin', 'Period End']]
    y_width = 5
    y_space = 1.25*y_width
    y_start = -y_width/2
    y_end = y_start
    yticks = []
    list_inst = df['Institution'].unique()
    for i in list_inst:
        df_inst = df[df['Institution'] == i]
        blocks = []
        for index, row in df_inst.iterrows():
            s = row['Period Begin']
            l = row['Period End']-s
            blocks.append([s, l])
        ax.broken_barh(blocks, (y_end, y_width), facecolors=inst_color(i))
        yticks.append(y_end+0.5*y_width)
        y_end = y_end + y_space

    ax.set_ylim(-y_space, y_end)
    ax.set_xlim(d_start, d_end)
    ax.set_xlabel('Date')
    ax.set_yticks(yticks)
    ax.set_yticklabels(list_inst)
    ax.set_title('Sourcefile periods')
    ax.grid(True)

    plt.show()


def spendingvscategory(df):
    start = df['Date'].min().date()
    end = df['Date'].max().date()
    msg = 'Data collected between\n{} and {}'.format(start, end)

    s = df.groupby(by=['Category']).sum()
    s = s.sort_values(by=['Amount'], ascending=False)

    fig, [ax1, ax2] = plt.subplots(1, 2)
    fig.suptitle('Spending by Category')
    fig.text(0.05, 0.05, msg, fontsize=8)

    ax1.pie(x=s['Amount'].abs(), labels=s.index)
    ax2.bar(s.index, s['Amount'].abs())
    plt.xticks(rotation='vertical')

    plt.show()


def paycheckcomparison(df1, df2, YTD=False):
    if YTD:
        PC1 = df1.payment_YTD
        PC2 = df2.payment_YTD
        title = 'Year to Date paycheck comparison'
    else:
        PC1 = df1.payment_regular
        PC2 = df2.payment_regular
        title = 'Single paycheck comparison'

    PC1_color = inst_color(df1.name)
    PC2_color = inst_color(df2.name)

    plt_cols = ['Regular Amount', 'Total Earnings', 'Total Net Pay']
    PC1 = PC1[plt_cols]
    PC2 = PC2[plt_cols]

    X = np.arange(max(PC1.size, PC2.size, len(plt_cols)))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(X + 0.00, PC1.iloc[0].fillna(0), color=PC1_color, width=0.25, label='iRobot')
    ax.bar(X + 0.25, PC2.iloc[0].fillna(0), color=PC2_color, width=0.25, label='ClearMotion')

    ax.set_ylabel('Amount ($)')
    ax.set_xlabel('Line Item')
    ax.set_title(title)
    ax.set_xticks(X)  # values
    ax.set_xticklabels(plt_cols, rotation='vertical')  # labels
    plt.subplots_adjust(bottom=0.4)
    plt.grid()
    ax.legend()
    plt.show()
