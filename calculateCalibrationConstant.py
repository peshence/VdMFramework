import csv
import datetime as dt
import json
import logging
import math
import pickle
import sys
import traceback
from collections import defaultdict

import numpy as np

import luminometers
from fitResultReader import fitResultReader
from luminometers import *
from vdmUtilities import makeCorrString

# [in Hz]
LHC_revolution_frequency =  11245

pi = math.pi

class XsecCalculationOptions:

    class LuminometerOptions:
        LuminometerTypes = ("HF", "PCC", "Vtx", "BCM1F", "PLT")
        WhatIsMeasured = ("CountsPerTime","Counts")
        NormalizationGraphs = ("None", "CurrentProduct")
        OldNormalizationAvailable = ("Yes", "No")

    class FormulaOptions:
        FormulaToUse = ("1D-Gaussian-like", "2D-like", "numerical-Integration")


def xsecFormula_1DGaussianLike(CapSigmaX, CapSigmaY, peakX, peakY):

    # units, want visible cross section in microbarn !
    CapSigmaX[0] =CapSigmaX[0]*1000
    CapSigmaX[1] =CapSigmaX[1]*1000
    CapSigmaY[0] =CapSigmaY[0]*1000
    CapSigmaY[1] =CapSigmaY[1]*1000

    # with approximation peakX ~ peakY ~ 0.5(peakX+peakY)
    xsec =  pi * CapSigmaX[0] * CapSigmaY[0] * (peakX[0] + peakY[0])
    xsecErr = ( CapSigmaX[1]*CapSigmaX[1]/CapSigmaX[0]/CapSigmaX[0] + \
                CapSigmaY[1]*CapSigmaY[1]/CapSigmaY[0]/CapSigmaY[0] + \
                (peakX[1]*peakX[1] + peakY[1]*peakY[1])/(peakX[0]+peakY[0])/(peakX[0]+peakY[0]))
    xsecErr = math.sqrt(xsecErr) * xsec

    return xsec, xsecErr

def xsecFormula_2DLike(fitResult):

    return xsec

def xsecFormula_numericalIntegration(fitFunc):    

    return xsec


def CalculateCalibrationConstant(configFile):

    # check that options chosen in json do actually exist

    # if non-standard luminometer chosen, check that all options provided are allowed, i.e. are in LuminometerOptions

    # either use xsec as returned by function, for "Counts", or xsec/LHC_frequency, for "CountsPerTime"


    config=open(configFile)
    ConfigInfo = json.load(config)
    config.close()

    Fill = ConfigInfo['Fill']
    AnalysisDir = ConfigInfo['AnalysisDir']
    Luminometer = ConfigInfo['Luminometer']
    Corr = ConfigInfo['Corr']
    InputFitResultsFile = ConfigInfo['InputFitResultsFile']
    fit = InputFitResultsFile.strip("FitResults.pkl")
    if 'CapSigmaInput' in ConfigInfo:
        CapSigmaInput = ConfigInfo['CapSigmaInput']
    corrFull = makeCorrString(Corr)
    InputFitResultsFile = './' + AnalysisDir + "/" + Luminometer + "/results/" + corrFull + "/" + InputFitResultsFile 
    OutputDir = './' + AnalysisDir + '/' + Luminometer + '/results/' + corrFull + '/'
    
    predefinedTypes = XsecCalculationOptions.LuminometerOptions.LuminometerTypes
    
    

    oldNormAvailable = False

    WhatIsMeasured = ConfigInfo['LuminometerSettings']['WhatIsMeasured']
    NormalizationGraphs = ConfigInfo['LuminometerSettings']['NormalizationGraphs']
    OldNormAvailable = ConfigInfo['LuminometerSettings']['OldNormAvailable']

    if Luminometer in predefinedTypes:
        defaults = LuminometerDefaults(Luminometer)
        if WhatIsMeasured == "default":
            WhatIsMeasured = defaults.WhatIsMeasured
        if NormalizationGraphs== "default":
            NormalizationGraphs = defaults.NormalizationGraphs
        if OldNormAvailable == "default":
            OldNormAvailable = defaults.OldNormAvailable
        print "defaults ", WhatIsMeasured, NormalizationGraphs, OldNormAvailable

    Total_inel_Xsec = ConfigInfo['Total_inel_Xsec']

    if OldNormAvailable:
        oldNormalization = ConfigInfo['OldNormalization']

        if oldNormalization < 0:
            print "Value of old normalization from json makes no sense, is negative, hence assume no old normalization available"
            OldNormAvailable = False

            #print "OldNormAvailable, oldNormalization", OldNormAvailable, oldNormalization

    FormulaToUse = ConfigInfo['FormulaToUse']
    Scanpairs = ConfigInfo['Scanpairs']

    fitResult = fitResultReader(InputFitResultsFile)
    
    CapSigmaDict = fitResult.getFitParam("CapSigma")
    CapSigmaErrDict = fitResult.getFitParam("CapSigmaErr")

    if 'CapSigmaInput' in ConfigInfo:
        fitResult2 = fitResultReader(CapSigmaInput)
        CapSigmaDict = fitResult2.getFitParam("CapSigma")
        CapSigmaErrDict = fitResult2.getFitParam("CapSigmaErr")
        
    peakDict = fitResult.getFitParam("peak")
    peakErrDict = fitResult.getFitParam("peakErr")

    fitstatusDict = fitResult.getFitParam("fitStatus")
    chi2Dict = fitResult.getFitParam("chi2")
    ndofDict = fitResult.getFitParam('ndof')
        
    table =[]
    csvtable = []
    csvtable.append(["XscanNumber_YscanNumber","Type", "BCID", "xsec", "xsecErr", "SBIL", 'SBILErr', 'inmean'])#, "normChange", "normChangeErr"] )
    table.append(["XscanNumber_YscanNumber","Type", "BCID", "xsec", "xsecErr", "SBIL", 'SBILErr', 'inmean'])#, "normChange", "normChangeErr"] )

    logbuffer="CalculateCalibrationConstant - excluded BCIDs\n"

    for entry in Scanpairs:

        XscanNumber = entry[0]
        YscanNumber = entry[1]
        XYbxlist=[]
        
        with open('./' + AnalysisDir + '/cond/BeamCurrents_' + str(Fill) + '.pkl') as f:
            beamdata = pickle.load(f)

        s1 = beamdata['Scan_' + str(XscanNumber)]
        b1 = [0 for i in range(3654)]
        b2 = [0 for i in range(3654)]
        bcx1 = {i[0]:i[1] for i in s1[len(s1)/2][-2].items()}
        bcx2 = {i[0]:i[1] for i in s1[len(s1)/2][-1].items()}



        s2 = beamdata['Scan_' + str(YscanNumber)]
        b1 = [0 for i in range(3654)]
        b2 = [0 for i in range(3654)]
        bcy1 = {i[0]:i[1] for i in s2[len(s2)/2][-2].items()}
        bcy2 = {i[0]:i[1] for i in s2[len(s2)/2][-1].items()}
        

        xsec = defaultdict(float)
        xsecErr = defaultdict(float)
        xsecDict = defaultdict(dict)
        xsecErrDict = defaultdict(dict)
        XscanID = 'Scan_'+str(XscanNumber)
        YscanID = 'Scan_'+str(YscanNumber)
        XY_ID = 'Scan_'+str(XscanNumber) + '_'+str(YscanNumber)

        logbuffer=logbuffer+"Scanpair:"+XY_ID+"\n"
        logbuffer=logbuffer+"BCIDs excluded because they are filled only in Scan_X or only in Scan_Y\n"
        logbuffer=logbuffer+"ScanID: list of excluded BCIDs\n"

        XexclBX=[]
        YexclBX=[]

        for bx in CapSigmaDict[XscanID]:
            if bx in CapSigmaDict[YscanID]:
                XYbxlist.append(bx)
            else:
                XexclBX.append(bx)

        for bx in CapSigmaDict[YscanID]:
            if bx not in CapSigmaDict[XscanID]:
                YexclBX.append(bx)
        temp = [int(i) for i in XYbxlist if i != 'sum']
        temp.sort()
        temp = [str(i) for i in temp]
        temp.append('sum')
        XYbxlist = temp
        logbuffer=logbuffer+XscanID+":"+str(XexclBX)+"\n"
        logbuffer=logbuffer+YscanID+":"+str(YexclBX)+"\n"

        chi2exclBX=[]
        logbuffer=logbuffer+"BCIDs excluded because chi2 is too high\n"    
        
        mean = []
        meanweights = []
        sbilmean = []
        sbilmeanweights = []
        for bx in XYbxlist:
            considerInMean = True
            #print "now at bx", bx
            CapSigmaX = [CapSigmaDict[XscanID][bx], CapSigmaErrDict[XscanID][bx]]
            CapSigmaY = [CapSigmaDict[YscanID][bx], CapSigmaErrDict[YscanID][bx]]
            peakX = [peakDict[XscanID][bx], peakErrDict[XscanID][bx]]
            peakY = [peakDict[YscanID][bx], peakErrDict[YscanID][bx]]

            # need to replace with something that takes FormulaToUse as argument and applies selected formula
            if FormulaToUse == "1D-Gaussian-like":
                value, err = xsecFormula_1DGaussianLike(CapSigmaX, CapSigmaY, peakX, peakY)
                if WhatIsMeasured == "CountsPerTime":
                    value =  value/LHC_revolution_frequency
                    err = err/LHC_revolution_frequency
                xsec[bx] =  value
                xsecErr[bx] = err

                if fitstatusDict[XscanID][bx] >0:
                    print "fitstatus Xscan for bx", bx, fitstatusDict[XscanID][bx]
                if fitstatusDict[YscanID][bx] >0:
                    print "fitstatus Yscan for bx", bx, fitstatusDict[YscanID][bx]
                 
                if bx =='sum' or chi2Dict[XscanID][bx]/ndofDict[XscanID][bx] >200:
                   print "chi2 Xscan for bx", bx, chi2Dict[XscanID][bx]
                   considerInMean = False
                if chi2Dict[YscanID][bx]/ndofDict[YscanID][bx] >200:
                   print "chi2 Yscan for bx", bx, chi2Dict[YscanID][bx]
                   considerInMean = False

                #printall(bx, CapSigmaX, CapSigmaY, peakX, peakY, xsec[bx], xsecErr[bx])
            
            sbil = (LHC_revolution_frequency*(peakX[0]*bcx1[bx]*bcx2[bx] + peakY[0]*bcy1[bx]*bcy2[bx]))/(1e22*2*xsec[bx])
            sbilerr = (LHC_revolution_frequency/(1e22*2*xsec[bx])) * math.sqrt(
                (peakX[1] * bcx1[bx]*bcx2[bx])**2 + (peakY[1] * bcy1[bx]*bcy2[bx])**2 +
                (xsecErr[bx] * (peakX[0]*bcx1[bx]*bcx2[bx] + peakY[0]*bcy1[bx]*bcy2[bx])/xsec[bx])**2)
            # normChange = -999. 
            # normChangeErr = -999.

            # print OldNormAvailable
            # print normChange
            # if OldNormAvailable:
            #     print 'wtf'
            #     normChange = LHC_revolution_frequency/xsec[bx] * 1/oldNormalization
            #     normChangeErr = normChange*xsecErr[bx]/xsec[bx]
            # print normChange
            row = [str(XscanNumber)+"_"+str(YscanNumber), "XY", bx, xsec[bx], xsecErr[bx], sbil, sbilerr, considerInMean]#, normChange, normChangeErr]
            if considerInMean:
                mean.append(xsec[bx])
                meanweights.append(xsecErr[bx]**(-2))
                sbilmean.append(sbil)
                sbilmeanweights.append(sbilerr**(-2))
            else:
                print "bcid ", bx, " excluded because chi2 value too high: ", chi2Dict[XscanID][bx]/ndofDict[XscanID][bx], chi2Dict[YscanID][bx]/ndofDict[YscanID][bx]
                chi2exclBX.append(bx)
            
            table.append(row)
            csvtable.append(row)
        # try:           
        #     if mean:
        #         av = np.average(mean, weights=meanweights)
        #         averr = np.sqrt(1/sum(meanweights))
        #         sbilav = np.average(sbilmean, weights=sbilmeanweights)
                
        #         sbilaverr = np.sqrt(1/sum(sbilmeanerr))
        #         avrow = [str(XscanNumber)+"_"+str(YscanNumber), "XY",'wav', av, averr, sbilav, sbilaverr, False]
        #         table.append(avrow)
        #         csvtable.append(avrow)
        # except ZeroDivisionError:
        #     message = 'Weights sum to zero (what?)' + '\n' + traceback.format_exc()
        #     print message
        #     logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
        #                         + '\n' + message)
            
        
        logbuffer=logbuffer+str(chi2exclBX)+"\n"
    # need to name output file such that fit function name in file name


    csvfile = open(OutputDir+'/LumiCalibration_'+ Luminometer+ '_'+ fit + str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()


    with open(OutputDir+'/LumiCalibration_'+ Luminometer+ '_'+ fit + str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)

    excldata=open(OutputDir+'/LumiCalibration_'+ Luminometer+ '_'+ fit + str(Fill)+'.log','w')
    excldata.write(logbuffer)
    excldata.close()

    return csvtable
       

if __name__ == '__main__':
    configFile = sys.argv[1]
    logging.basicConfig(filename="Automation/Logs/calibrationconst_" +
                            dt.datetime.now().strftime('%y%m%d%H%M%S') + '.log', level=logging.DEBUG)
    CalculateCalibrationConstant(configFile)
