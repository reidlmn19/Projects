import os
import pandas as pd

main_directory = os.path.dirname(os.path.realpath(__file__))
path_colorLib = '/'.join([main_directory,'CrayolaColorLibrary.csv'])

df_colorLib = pd.read_csv(path_colorLib, index_col="Name")
print(df_colorLib)