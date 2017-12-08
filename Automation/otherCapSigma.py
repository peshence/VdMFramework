import pandas as pd
import os
import math
import numpy as np

analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationLengthScale/Analysed_Data/'
scans = os.listdir(analysisdir)
detectors = ['PLT','BCM1FPCVD', 'HFET','HFOC']
maindet = 'BCM1FPCVD'
def fit(det, name):
    return ('S' if name == '6016_28Jul17_055855_28Jul17_060210' else 'D') + ('G' if det == 'PLT' else 'GConst')

d = {}
for scan in scans:
    df = pd.DataFrame()
    if scan[:4] != '6016': continue
    d[scan] = {}
    for det in os.listdir(analysisdir + scan):
        if det not in detectors: continue
        curdf = pd.DataFrame.from_csv(analysisdir + scan + '/' + det + '/results/BeamBeam/' + fit(det,scan) + '_FitResults.csv')#.loc[:,['CapSigma','CapSigmaErr','peak','peakErr']]
        
        boo = curdf.Type.tolist()[0] == 'Y'
        curdfx = curdf.loc[2 if boo else 1,['BCID','CapSigma','CapSigmaErr','peak','peakErr']]
        curdfy = curdf.loc[1 if boo else 2,['BCID','CapSigma','CapSigmaErr','peak','peakErr']]
        curdfx.index = curdfx.BCID
        curdfy.index = curdfx.BCID
        curdfx.columns = [('X_' if i!='BCID' else '') + i for i in curdfx.columns]
        curdfy.columns = [('Y_' if i!='BCID' else '') + i for i in curdfy.columns]

        d[scan][det] = pd.concat([curdfx, curdfy],axis=1)

dav = {}
for scan in d:
    dav[scan] = {}
    dav[scan + 'Err'] = {}
    detb = d[scan][maindet]
    for detn in d[scan]:
        det = d[scan][detn]
        det['xsec'] = math.pi * det.X_CapSigma * det.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
        det['xsecErr'] = det.xsec * np.sqrt((det.X_CapSigmaErr/det.X_CapSigma)**2 + \
                         (det.Y_CapSigmaErr/det.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)

        det['BCM1Fxsec'] = math.pi * detb.X_CapSigma * detb.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
        det['BCM1FxsecErr'] = det.BCM1Fxsec * np.sqrt((detb.X_CapSigmaErr/detb.X_CapSigma)**2 + \
                         (detb.Y_CapSigmaErr/detb.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)
        det.to_csv(detn + '_' + scan + '.csv')
        dav[scan][detn] = np.mean(det['BCM1Fxsec'])
        dav[scan + 'Err'][detn] = np.mean(det['BCM1FxsecErr'])
pd.DataFrame.from_dict(dav).to_csv('avBCapsigma.csv')