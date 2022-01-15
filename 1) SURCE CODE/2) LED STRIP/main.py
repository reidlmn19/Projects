import os
import pandas as pd

main_directory = os.path.dirname(os.path.realpath(__file__))
color_str = 'Macaroni and Cheese'

def set_LEDColor(color, lookup=None):
    ind = str(color)
    
    if lookup:
        df_colorLib = pd.read_csv(lookup, index_col="Name")
    else:
        path_colorLib = '/'.join([main_directory,'CrayolaColorLibrary.csv'])
        df_colorLib = pd.read_csv(path_colorLib, index_col="Name")
    
    if ind in df_colorLib.index:
        h_color = df_colorLib.loc[ind]['Hexidecimal']
    else:
        print('Color not found')
        h_color = None
    return h_color

def hexToRGB(h):
    r = int(h[0:2],16)
    g = int(h[2:4],16)
    b = int(h[4:6],16)
    return [r,g,b]

color_h = set_LEDColor(color_str)
print(hexToRGB(color_h))
