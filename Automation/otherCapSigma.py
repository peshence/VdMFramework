import pandas as pd
import os
import math
import numpy as np
import scipy.stats as stats

analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationMinuit/Analysed_Data/'
scans = os.listdir(analysisdir)
detectors = ['PLT','BCM1FPCVD', 'HFET','HFOC']
corrs = ['noCorr','BeamBeam','BeamBeam_LengthScale']
maindet = 'BCM1FPCVD'
# weighted = True
def fit(det, name, const):
    return ('S' if name == '6016_28Jul17_055855_28Jul17_060210' else 'D') + ('G' if (not const or det == 'PLT') else 'GConst')

def do(const):
    d = {}
    end = ('c' if const else '') + '.csv' 
    for corr in corrs:
        for scan in scans:
            df = pd.DataFrame()
            if scan[:4] != '6016' or scan == '6016_28Jul17_055855_28Jul17_060210' or scan == '6016_28Jul17_152753_28Jul17_155019': continue
            d[scan] = {}
            for det in os.listdir(analysisdir + scan):
                if det not in detectors: continue
                curdf = pd.DataFrame.from_csv(analysisdir + scan + '/' + det + '/results/' + corr + '/' + fit(det,scan,const) + '_FitResults.csv')#.loc[:,['CapSigma','CapSigmaErr','peak','peakErr']]

                boo = curdf.Type.tolist()[0] == 'Y'
                curdfx = curdf.loc[2 if boo else 1,['BCID','CapSigma','CapSigmaErr','peak','peakErr','covStatus']]
                curdfy = curdf.loc[1 if boo else 2,['CapSigma','CapSigmaErr','peak','peakErr','covStatus']]
                curdfx.index = curdfx.BCID
                curdfy.index = curdfx.BCID
                converged = (curdfx.covStatus == 3) & (curdfy.covStatus==3)
                curdfx = curdfx[converged]
                curdfy = curdfy[converged]
                curdfx.columns = [('X_' if i!='BCID' else '') + i for i in curdfx.columns]
                curdfy.columns = [('Y_' if i!='BCID' else '') + i for i in curdfy.columns]

                d[scan][det] = pd.concat([curdfx, curdfy],axis=1)

        dav = {}
        bdav = {}
        wdav = {}
        wbdav = {}
        capxwav = {}
        capywav = {}
        peakxwav = {}
        peakywav = {}
        for scan in d:
            dav[scan] = {}
            dav[scan + 'Err'] = {}
            dav[scan + 'n'] = {}
            
            bdav[scan] = {}
            bdav[scan + 'Err'] = {}
            bdav[scan + 'n'] = {}
            
            wdav[scan] = {}
            wdav[scan + 'Err'] = {}
            wdav[scan + 'n'] = {}
            
            wbdav[scan] = {}
            wbdav[scan + 'Err'] = {}
            wbdav[scan + 'n'] = {}

            capxwav[scan] = {}
            capxwav[scan + 'Err'] = {}
            capxwav[scan + 'n'] = {}

            capywav[scan] = {}
            capywav[scan + 'Err'] = {}
            capywav[scan + 'n'] = {}

            peakxwav[scan] = {}
            peakxwav[scan + 'Err'] = {}
            peakxwav[scan + 'n'] = {}

            peakywav[scan] = {}
            peakywav[scan + 'Err'] = {}
            peakywav[scan + 'n'] = {}
            
            detb = d[scan][maindet]
            for detn in d[scan]:
                det = d[scan][detn]

                capxwav[scan][detn], sumw = np.average(det.X_CapSigma,weights=[1/i**2 for i in det.X_CapSigmaErr], returned=True)
                capxwav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                capxwav[scan + 'n'][detn] = len(np.isfinite(det.X_CapSigma))

                capywav[scan][detn], sumw = np.average(det.Y_CapSigma,weights=[1/i**2 for i in det.Y_CapSigmaErr], returned=True)
                capywav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                capywav[scan + 'n'][detn] = len(np.isfinite(det.Y_CapSigma))

                peakxwav[scan][detn], sumw = np.average(det.X_peak,weights=[1/i**2 for i in det.X_peakErr], returned=True)
                peakxwav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                peakxwav[scan + 'n'][detn] = len(np.isfinite(det.X_peak))

                peakywav[scan][detn], sumw = np.average(det.Y_peak,weights=[1/i**2 for i in det.Y_peakErr], returned=True)
                peakywav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                peakywav[scan + 'n'][detn] = len(np.isfinite(det.Y_peak))

                det['xsec'] = math.pi * det.X_CapSigma * det.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
                det['xsecErr'] = det.xsec * np.sqrt((det.X_CapSigmaErr/det.X_CapSigma)**2 + \
                                (det.Y_CapSigmaErr/det.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)

                det['BCM1Fxsec'] = math.pi * detb.X_CapSigma * detb.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
                det['BCM1FxsecErr'] = det.BCM1Fxsec * np.sqrt((detb.X_CapSigmaErr/detb.X_CapSigma)**2 + \
                                (detb.Y_CapSigmaErr/detb.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)
                det.to_csv('DG' + ('Const/' if const else '/') +detn + '_' + scan + '_' + corr + end, index=False)
                
                wbdav[scan][detn], sumw = np.average(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'],weights=[1/i**2 for i in det[np.isfinite(det.BCM1Fxsec)]['BCM1FxsecErr']], returned=True)
                wbdav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                wbdav[scan + 'n'][detn] = len(np.isfinite(det.BCM1Fxsec))

                bdav[scan][detn] = np.mean(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'])
                bdav[scan + 'Err'][detn] = stats.sem(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'])
                bdav[scan + 'n'][detn] = len(np.isfinite(det.BCM1Fxsec))

                wdav[scan][detn], sumw = np.average(det['xsec'],weights=[1/i**2 for i in det['xsecErr']], returned=True)
                wdav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                wdav[scan + 'n'][detn] = len(np.isfinite(det.xsec))

                dav[scan][detn] = np.mean(det['xsec'])
                dav[scan + 'Err'][detn] = stats.sem(det['xsec'])
                dav[scan + 'n'][detn] = len(np.isfinite(det.xsec))

            pd.DataFrame.from_dict(wbdav).to_csv('DG' + ('Const/' if const else '/') +'avwBCapsigma_' + corr + end)
            pd.DataFrame.from_dict(wdav).to_csv('DG' + ('Const/' if const else '/') +'avw_' + corr + end)

            pd.DataFrame.from_dict(bdav).to_csv('DG' + ('Const/' if const else '/') +'avBCapsigma_' + corr + end)
            pd.DataFrame.from_dict(dav).to_csv('DG' + ('Const/' if const else '/') +'av_' + corr + end)
            
            pd.DataFrame.from_dict(capxwav).to_csv('DG' + ('Const/' if const else '/') +'capXwav_' + corr + end)
            pd.DataFrame.from_dict(capywav).to_csv('DG' + ('Const/' if const else '/') +'capYwav_' + corr + end)
            
            pd.DataFrame.from_dict(peakxwav).to_csv('DG' + ('Const/' if const else '/') +'peakXwav_' + corr + end)
            pd.DataFrame.from_dict(peakywav).to_csv('DG' + ('Const/' if const else '/') +'peakYwav_' + corr + end)


do(True)
do(False)