import json
import re
import os
import numpy as np
import scipy.stats as stats
import pandas as pd
import datetime as dt


jsonFileName = r"C:\Users\ptsrunch\OneDrive\CERN\Technical\VdM offline automation\VdM\sbil.json"

jsonFile = open(jsonFileName, 'r')
jsonData = jsonFile.read()
sigma = json.loads(jsonData[3:])
folder = 'Analysed_Data/'
lumis = ["PLT", "HFET", "HFOC", 'BCM1F', "BCM1FSI", "BCM1FPCVD", "BCM1FSCVD"]
lumis = ["BCM1FPCVD"]
fillr = 'output(\d+).*\.json'


dirs = [i for i in os.listdir(folder) if i[0] != 'F' and int(i[:4]) >= 5930]
keys = ['timestamp', 'fill', 'sbil']
cols = keys + lumis
df = pd.DataFrame(columns = cols)

for dir in dirs:
    
    jsons = [i for i in os.listdir(folder + '/' + dir) if i[-4:] == 'json' and lumi in i]
    # if lumi == 'HFLumi':
    #     jsons = [i for i in jsons if 'HFLumiET' not in i]
    row = {}
    for j in jsons:
        j = json.load(open(folder + dir + '/' +j,'r'))
        
        if not any([lumi in j for lumi in lumis]:
            continue
        fitr = 'output\d+' + lumi + '(.*).json'
        fit = re.match(fitr,j).group(1)
        fill = re.match(fillr,j).group(1)
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

