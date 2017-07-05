import pandas as pd
import os
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-f','--folder')
args = parser.parse_args()
folder = args.folder
df = pd.DataFrame(columns=['correction[%]','CapSigmaY','CapSigmaX','Product','PeakX','PeakY','SigmaVis'])
"""Sbil correction script summary script"""
for l in os.listdir(folder):
    if l[-2]!='f':
        continue
    try:
        check = int(l[-1])
    except:
        continue
    fitres = pd.read_csv(folder + l +'/results/BeamBeam/SG_FitResults.csv')
    fitres = fitres.loc[(fitres.BCID != 'sum') & (fitres.BCID!='wav')]
    csx = np.mean(fitres.loc[fitres.Type == 'X'].CapSigma)
    csy = np.mean(fitres.loc[fitres.Type == 'Y'].CapSigma)
    px = np.mean(fitres.loc[fitres.Type == 'X'].peak)
    py = np.mean(fitres.loc[fitres.Type == 'Y'].peak)

    calib = pd.read_csv(folder+l+ '/results/BeamBeam/LumiCalibration_' + l + '_SG_5848.csv')
    sigmavis = np.mean(calib.loc[(calib.BCID != 'sum') & (calib.BCID != 'wav')].xsec)
    df.loc[check] = [-2+0.5*(check),csx,csy,csx*csy,px,py,sigmavis]

df.to_csv(folder[14:-1]+'f.csv')