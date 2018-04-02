import json
import os
import pandas
import numpy as np

folder = '/brildata/vdmoutput/AutomationBackgroundCorrection2/Analysed_Data/6016_28Jul17_100134_28Jul17_102201/'
luminometers = ['PLT', 'BCM1FPCVD', 'HFOC']
data = {}
for ratefile in os.listdir(folder + 'LuminometerData/'):
    for luminometer in luminometers:
        data[luminometer] = {}
        with open(folder + 'LuminometerData/Rates_' + luminometer + '_6016.json' ) as f:
            j = json.load(f)
            print j['Scan_1'][13]
            data[luminometer]['Rate'] = np.mean(j['Scan_1'][12]['Rates'].values())
    for luminometer in luminometers:
        with open(folder + '/corr/Background_' + luminometer + '_6016.json' ) as f:
            j = json.load(f)
            data[luminometer]['Background'] = j['background']
            data[luminometer]['BackgroundError'] = j['backgroundError']

pandas.DataFrame.from_dict(data).to_csv('bg6016scan1.csv')
