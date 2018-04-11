import json
import matplotlib.pyplot as plot
import csv
import os
import argparse
import pandas as pd
import numpy as np
from itertools import combinations

folder = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBackgroundCorrection/Analysed_Data/'

scanpair = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBackgroundCorrection/Analysed_Data/6016_28Jul17_100134_28Jul17_102201/'

lumis = ['PLT', 'HFET']
lumi1bg = 2.3396306874090556e-06 #should be a dictionary with all backgrounds

def loadData(scanpair,lumis):
    rates = {}

    for lumi in lumis:
        rates[lumi] = json.load(open(scanpair + '/LuminometerData/Rates_' + lumi + '_6016.json'))

    for nlumi1,nlumi2 in combinations(lumis,2):
        lumi1 = rates[nlumi1]
        lumi2 = rates[nlumi2]
        ratios = {bx:[] for bx in lumi1['Scan_1'][0]['Rates'].keys()}
        ratios[nlumi1+'Rates'] = []
        for scan in lumi1.keys():
            if 'Scan' not in scan: continue
            for step1,step2 in zip(lumi1[scan],lumi2[scan]):
                ratios[nlumi1+'Rates'].append(np.mean(step1['Rates'].values())-lumi1bg)
                for bx in step1['Rates'].keys():
                    ratios[bx].append(0 if not step2['Rates'][bx] else (step1['Rates'][bx]-lumi1bg)/step2['Rates'][bx])

        json.dump(ratios, open(nlumi1 + nlumi2 + '_RRratiosBG.json','w'))
        pd.DataFrame.from_dict(ratios).to_csv(nlumi1 + nlumi2 + '_RRratiosBG.csv')

loadData(scanpair,lumis)
# def plot(ratios):
#     for ratio in ratios: