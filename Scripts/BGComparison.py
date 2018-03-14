import json
import os
import pandas

folder = '/brildata/vdmoutput/AutomationBackground/Analysed_Data/'
luminometers = ['PLT', 'BCM1FPCVD', 'HFOC']
data = {}
for l in luminometers:
    data[l] = []
    data[l+'Err'] = []
for scanfolder in os.listdir(folder):
    for luminometer in luminometers:
        with open(folder + scanfolder + '/LuminometerData/Rates_' + luminometer + '_6016.json' ) as f:
            j = json.load(f)
            data[luminometer].append(j['backgroundApplied'])
            data[luminometer+'Err'].append(j['backgroundError'])

pandas.DataFrame.from_dict(data).to_csv('bgcomparison.csv')
