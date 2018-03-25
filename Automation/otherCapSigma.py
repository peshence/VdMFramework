import pandas as pd
import os
import math
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plot

detectors = ['PLT','BCM1FPCVD', 'HFET','HFOC']
corrs = ['noCorr','BeamBeam','BeamBeam_LengthScale']
maindet = 'PLT'
# weighted = True
def fit(det, name, const):
    return ('S' if name == '6016_28Jul17_055855_28Jul17_060210' else 'D') + ('G' if (not const or det == 'PLT') else 'GConst')


def do(const, analysisdir, end, finaldir):
    scans = os.listdir(analysisdir)
    if not os.path.isdir('DG' + finaldir):
        os.mkdir('DG' + finaldir)
    for corr in corrs:
        allscans = {}
        allscansfull = {}
        scannum = -1
        for det in detectors:
            allscans[det] = pd.DataFrame()
            allscansfull[det] = pd.DataFrame()
        d = {}
        for scan in scans:
            df = pd.DataFrame()
            if scan[:4] != '6016' or scan == '6016_28Jul17_152753_28Jul17_155019': continue # scan == '6016_28Jul17_055855_28Jul17_060210' or
            scannum = scannum+1
            d[scan] = {}
            for det in os.listdir(analysisdir + scan):
                if det not in detectors: continue
                try:
                    curdf = pd.DataFrame.from_csv(analysisdir + scan + '/' + det + '/results/' + corr + '/' + fit(det,scan,const) + '_FitResults.csv')#.loc[:,['CapSigma','CapSigmaErr','peak','peakErr']]
                except:
                    curdf = pd.DataFrame.from_csv(analysisdir + scan + '/' + det + '/results/' + corr + '/' + fit(det,scan,const) + 'Const' + '_FitResults.csv')
                boo = curdf.Type.tolist()[0] == 'Y'
                columns = ['CapSigma','CapSigmaErr','peak','peakErr'] + (['Const','ConstErr'] if const else []) + ['covStatus']
                curdfx = curdf.loc[2 if boo else 1, ['BCID'] + columns]
                curdfy = curdf.loc[1 if boo else 2, columns]
                curdfx.index = curdfx.BCID
                curdfy.index = curdfx.BCID
                curdfx.columns = [('X_' if i!='BCID' else '') + i for i in curdfx.columns]
                curdfy.columns = [('Y_' if i!='BCID' else '') + i for i in curdfy.columns]

                fullxydf = pd.concat([curdfx, curdfy],axis=1)
                converged = (fullxydf.X_covStatus == 3) & (fullxydf.Y_covStatus==3)
                # curdfx = curdfx[converged]
                # curdfy = curdfy[converged]

                # xydf = pd.concat([curdfx, curdfy],axis=1)
                xydf = fullxydf[converged]
                d[scan][det] = xydf

                xydf['scan'] = pd.Series([scannum for i in xydf.BCID], index=xydf.index)
                fullxydf['scan'] = pd.Series([scannum for i in fullxydf.BCID], index=fullxydf.index)
                # allscans[det] = allscans[det].append(xydf.assign(scantime=pd.Series([scan for row in xydf.BCID])))
                allscans[det] = allscans[det].append(xydf)
                allscansfull[det] = allscansfull[det].append(fullxydf)


        dav = {}
        bdav = {}
        wdav = {}
        wbdav = {}
        capxwav = {}
        capywav = {}
        peakxwav = {}
        peakywav = {}
        constxwav = {}
        constywav = {}
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

            constxwav[scan] = {}
            constxwav[scan + 'Err'] = {}
            constxwav[scan + 'n'] = {}

            constywav[scan] = {}
            constywav[scan + 'Err'] = {}
            constywav[scan + 'n'] = {}
            
            detb = d[scan][maindet]
            for detn in d[scan]:
                det = d[scan][detn]
                print detn,scan
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

                if const:
                    constxwav[scan][detn], sumw = np.average(det.X_Const,weights=[1/i**2 for i in det.X_ConstErr], returned=True)
                    constxwav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                    constxwav[scan + 'n'][detn] = len(np.isfinite(det.X_Const))

                    constywav[scan][detn], sumw = np.average(det.Y_Const,weights=[1/i**2 for i in det.Y_ConstErr], returned=True)
                    constywav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                    constywav[scan + 'n'][detn] = len(np.isfinite(det.Y_Const))

                det['xsec'] = math.pi * det.X_CapSigma * det.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
                det['xsecErr'] = det.xsec * np.sqrt((det.X_CapSigmaErr/det.X_CapSigma)**2 + \
                                (det.Y_CapSigmaErr/det.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)

                det['BCM1Fxsec'] = math.pi * detb.X_CapSigma * detb.Y_CapSigma * (det.X_peak + det.Y_peak) * 1e6
                det['BCM1FxsecErr'] = det.BCM1Fxsec * np.sqrt((detb.X_CapSigmaErr/detb.X_CapSigma)**2 + \
                                (detb.Y_CapSigmaErr/detb.Y_CapSigma)**2 + (det.X_peakErr**2 + det.Y_peakErr**2)/(det.X_peak + det.Y_peak)**2)
                det.to_csv('DG' + finaldir +detn + '_' + scan + '_' + corr + end, index=False)
                
                wbdav[scan][detn], sumw = np.average(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'],weights=[1/i**2 for i in det[np.isfinite(det.BCM1Fxsec)]['BCM1FxsecErr']], returned=True)
                wbdav[scan + 'Err'][detn] = 1/np.sqrt(sumw)
                wbdav[scan + 'n'][detn] = len(np.isfinite(det.BCM1Fxsec))

                bdav[scan][detn] = np.mean(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'])
                bdav[scan + 'Err'][detn] = stats.sem(det[np.isfinite(det.BCM1Fxsec)]['BCM1Fxsec'])
                bdav[scan + 'n'][detn] = len(np.isfinite(det.BCM1Fxsec))

                wdav[scan][detn], sumw = np.average(det['xsec'],weights=[1/i**2 for i in det['xsecErr']], returned=True)
                wdav[scan + 'Err'][detn] = np.std(det.xsec)
                wdav[scan + 'n'][detn] = len(np.isfinite(det.xsec))

                dav[scan][detn] = np.mean(det['xsec'])
                dav[scan + 'Err'][detn] = stats.sem(det['xsec'])
                dav[scan + 'n'][detn] = len(np.isfinite(det.xsec))

        pd.DataFrame.from_dict(wbdav).to_csv('DG' + finaldir +'avwBCapsigma_' + corr + end)
        pd.DataFrame.from_dict(wdav).to_csv('DG' + finaldir +'avw_' + corr + end)

        pd.DataFrame.from_dict(bdav).to_csv('DG' + finaldir +'avBCapsigma_' + corr + end)
        pd.DataFrame.from_dict(dav).to_csv('DG' + finaldir +'av_' + corr + end)
        
        pd.DataFrame.from_dict(capxwav).to_csv('DG' + finaldir +'capXwav_' + corr + end)
        pd.DataFrame.from_dict(capywav).to_csv('DG' + finaldir +'capYwav_' + corr + end)
        
        pd.DataFrame.from_dict(peakxwav).to_csv('DG' + finaldir +'peakXwav_' + corr + end)
        pd.DataFrame.from_dict(peakywav).to_csv('DG' + finaldir +'peakYwav_' + corr + end)
            
        if const:
            pd.DataFrame.from_dict(constxwav).to_csv('DG' + finaldir +'constXwav_' + corr + end)
            pd.DataFrame.from_dict(constywav).to_csv('DG' + finaldir +'constYwav_' + corr + end)

        for detector in allscans:
            allscans[detector].to_csv('DG' + finaldir +'allscans_' + detector + corr + end, index=False)
            allscansfull[detector].to_csv('DG' + finaldir +'allscansfull_' + detector + corr + end, index=False)
            # if corr=='BeamBeam_LengthScale' and const:
            #     for scan in set(allscansfull[detector].scan):
            #         plotdf = allscansfull[detector][allscansfull[detector].scan == scan]
            #         plot.title(detector + ' Const per scan, peak (roughly) ' + str(peakxwav[sorted([i for i in peakxwav.keys() if i[-1]!='n' and not 'Err' in i])[scan-1]][detector]))
            #         # plot.errorbar(plotdf.BCID, plotdf.X_Const + plotdf.Y_Const, plotdf.X_ConstErr + plotdf.Y_ConstErr, label='Scan ' + str(scan))
            #         plot.plot(plotdf.BCID, plotdf.X_Const + plotdf.Y_Const, label='Scan ' + str(scan))            
            #     plot.legend()
            #     plot.show()


# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationMinuit/Analysed_Data/'

# end = 'c' + '.csv'
# finaldir = 'Const/'
# do(True,analysisdir)
# end = '.csv'
# finaldir = '/'
# do(False,analysisdir)

# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationConstTest/Analysed_Data/'
# end = 'cc' + '.csv'
# finaldir = 'ConstConst/'
# do(True,analysisdir)

# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBGTest/Analysed_Data/'
# end = 'bc' + '.csv'
# finaldir = 'BG/'
# do(False,analysisdir)

# end = 'bu' + '.csv'
# finaldir = 'BU/'
# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBGUnconstrainedTest/Analysed_Data/'
# do(False,analysisdir,end,finaldir)

# end = 'b2semacc' + '.csv'
# finaldir = 'B2semacc/'
# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBackgroundErrSemAccounted/Analysed_Data/'
# do(False,analysisdir,end,finaldir)

# end = 'b2stdacc' + '.csv'
# finaldir = 'B2stdacc/'
# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBackgroundErrStdAccounted/Analysed_Data/'
# do(False,analysisdir,end,finaldir)


# analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationMinuit/Analysed_Data/'
# end = '.csv'
# finaldir = 'B2std/'
# do(False,analysisdir,end,finaldir)


end = 'bgcorrection' + '.csv'
finaldir = 'bgcorrection/'
analysisdir = '/cmsnfsbrildata/brildata/vdmoutput/AutomationBackgroundCorrection/Analysed_Data/'
do(False,analysisdir,end,finaldir)
