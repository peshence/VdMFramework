import postvdm
import pandas as pd
import pickle as pkl
import os
import re
import json

# automation = '/brildata/vdmoutput/Automation/'
automation = '/brildata/vdmoutput18/'
detectors = ['PLT','BCM1FPCVD','BCM1FSI','HFET','HFOC']
for scan in os.listdir(automation+'Analysed_Data/'):
    if os.path.exists(automation+'Analysed_Data/' +scan+'/cond/Scan_' + scan[:4] + '.pkl'):
        with open(automation+'Analysed_Data/' +scan+'/cond/Scan_' + scan[:4] + '.pkl') as pf:
            scanfile = pkl.load(pf)
    else:
        with open(automation+'Analysed_Data/' +scan+'/cond/Scan_' + scan[:4] + '.json') as jf:
            scanfile = json.load(jf)
    for detector in detectors:
        try:
            if detector=='BCM1FPCVD' and not os.path.exists(automation+'Analysed_Data/'+scan+'/'+detector):
                detector = 'BCM1F'
            files = os.listdir(automation+'Analysed_Data/'+scan+'/'+detector+'/results/BeamBeam/')
            lumicals = [f for f in files if 'LumiCalibration' in f and 'pkl' in f]
            for lumical in lumicals:
                fit = re.match('LumiCalibration_[A-Z1]*_([A-Za-z]*)_\d{4}\.pkl',lumical).groups()[0]
                
                fitres = fit+'_FitResults.pkl'
                with open(automation+'Analysed_Data/'+scan+'/'+detector+'/results/BeamBeam/'+fitres) as tempfile:
                    temp = pkl.load(tempfile)
                fits = pd.DataFrame(temp[1:],columns=temp[0])
                with open(automation+'Analysed_Data/'+scan+'/'+detector+'/results/BeamBeam/'+lumical) as tempfile:
                    temp = pkl.load(tempfile)
                cals = pd.DataFrame(temp[1:],columns=temp[0])
                postvdm.PostOutput(fits,cals,scanfile['ScanTimeWindows'],int(scanfile['Fill']),\
                    scanfile['Run'][0],False,scan,detector,fit,scanfile['Angle'],\
                    automation_folder=automation,post=True)
        except Exception as e:
            print(e)
            # print fit, scan, detector
