import json
import re
import os
import numpy as np
import scipy.stats as stats
import pandas as pd
import datetime as dt


folder = 'Analysed_Data/'
lumis = ['PLT','HFLumi', 'BCM1F', 'HFLumiET']
fillr = 'output(\d+).*\.json'


dirs = [i for i in os.listdir(folder) if i[0] != 'F' and int(i[:4]) >= 5718]
cols = ['timestamp', 'fill', 'filledbunches', 'fit', 'peak_x_bx','peak_x_bx_stdev', 'capsigma_x_bx','capsigma_x_bx_stdev', 'peak_y_bx','peak_y_bx_stdev', 'capsigma_y_bx','capsigma_y_bx_stdev', 'sigmavis_bx','sigmavis_bx_stdev']

for lumi in lumis:
    df = pd.DataFrame(columns = cols)
    fitr = 'output\d+' + lumi + '(.*).json'
    for dir in dirs:
        
        jsons = [i for i in os.listdir(folder + '/' + dir) if i[-4:] == 'json' and lumi in i]
        if lumi == 'HFLumi':
            jsons = [i for i in jsons if 'HFLumiET' not in i]
        for j in jsons:
            fit = re.match(fitr,j).group(1)
            fill = re.match(fillr,j).group(1)
            j = json.load(open(folder + dir + '/' +j,'r'))
            row = {}
            key=cols[0]
            row.update({key:dt.datetime.fromtimestamp(j[key])})
            key = cols[1]
            row.update({key:int(j[key])})
            key = cols[2]
            row.update({key:len([i for i in j[cols[-2]] if i != 0])})
            key = cols[3]
            row.update({key:fit})
            for key in cols[4::2]:
                #if 'stdev' not in key:
                data = []
                data = [i for i in j[key] if i != 0]
                row.update({key:np.mean(data)})
                row.update({key + '_stdev':stats.sem(data)})
                
            df = df.append(row, ignore_index=True)
    df.sort_values(by='timestamp',inplace=True)
    df.to_csv(lumi + '_table.csv',index=False)

