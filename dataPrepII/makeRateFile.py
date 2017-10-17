import ROOT as r

import tables
import numpy as np
from scipy import stats
import pandas as pd

import json
import os
import datetime as dt


def getRates(datapath, rateTable, scanpt, fill):
    '''Gets the data in the corresponding folder or hd5 file for the respective ratetable and scan point'''
    # print "beginning of getCurrents", scanpt

    bxdata = []
    avgdata = []
    bxdf = pd.DataFrame()
    avgdf = pd.DataFrame()

    rates = {}
    ratesErr = {}
    collBunches=[]

    # omit very first nibble because it may not be fully contained in VdM scan
    tw = '(timestampsec >' + str(scanpt[0]) + ') & (timestampsec <=' +  str(scanpt[1]) + ')'
    def readh5(filename, bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches):
        beamtable = None
        with tables.open_file(filename, 'r') as h5file:
            for table in h5file.root:
                if table.name == rateTable:
                    beamtable = table
                    break
            if not beamtable:
                print 'No table name ' + rateTable + ' in this file - ' + filename
                return bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches
 
                
            # sum over all bx
            if rateTable != 'pltslinklumi':
                table = [(r['avgraw'], r['bxraw']) for r in beamtable.where(tw)]
                avglist = [r[0] for r in table]
                if avglist:
                    avgdata = avgdata + avglist
                # rates per bx 
                bxlist = [r[1] for r in table]
            else:
                avglist = [r['avgraw'] for r in beamtable.where(tw)]
                
                if avglist:
                    avgdata = avgdata + avglist
                # rates per bx 
                bxlist = [[r for i in range(3564)] for r in avglist]

            if bxlist:
                bxdata = bxdata + bxlist

            removestrays = lambda a: np.array([0 if i < 6e9 else 1 for i in a])
            table = [(removestrays(r['bxintensity1']), removestrays(r['bxintensity2'])) for r in h5file.root.beam.where(tw)]
            bunchlist1 = [r[0] for r in table] 
            bunchlist2 = [r[1] for r in table] 

            if bunchlist1 and bunchlist2:
                collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
        return bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches
    if datapath[-4:] == '.hd5':
        bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches = readh5(datapath, bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches)
    else:        
        filelist = os.listdir(datapath)
        for file in filelist:
            if str.isdigit(str(file[0])) and int(file[:4]) == int(fill):
                bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches = readh5(datapath + '/' + file, bxdata, avgdata, bxdf, avgdf, rates, ratesErr, collBunches)

    bxdf = pd.DataFrame(bxdata)
    avgdf = pd.DataFrame(avgdata)

    #rates for colliding bunches
    if bxdf.empty:
        print "Attention, rates bxdf empty because timestamp window not contained in file"
    else:
        for idx, bcid in enumerate(collBunches):
            i = bcid if int(fill)>=5838 or rateTable != 'hfetlumi' else (bcid-1 if bcid!=0 else 3563)
            rates[str(bcid+1)] = bxdf[i].mean()
            ratesErr[str(bcid+1)] = stats.sem(bxdf[i])

    if avgdf.empty:
        print "Attention, rates avgdf empty because timestamp window not contained in file"
    else:
        rates['sum'] = avgdf[0].mean()
        ratesErr['sum'] = stats.sem(avgdf[0])

    return (rates, ratesErr)


def doMakeRateFile(ConfigInfo):
    
    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    InputScanFile = AnalysisDir + "/" + str(ConfigInfo['InputScanFile'])
    InputLumiDir = str(ConfigInfo['InputLumiDir'])
    RateTable = str(ConfigInfo['RateTable'])

    with open(InputScanFile, 'rb') as f:
        scanInfo = json.load(f)

    table = {}

    for i, name in enumerate(scanInfo["ScanNames"]):
        key = "Scan_" + str(i+1)        
        scanpoints = scanInfo[key]
        table[key]=[]
        for j, sp in enumerate(scanpoints):
            rates = getRates(InputLumiDir, RateTable, sp[3:],scanInfo["Fill"])
            scanpoint = {}
            scanpoint.update({'ScanNumber':i+1})
            scanpoint.update({'ScanName':name})
            scanpoint.update({'ScanPoint':j+1})
            scanpoint.update({'Rates':rates[0]})
            scanpoint.update({'RateErrs':rates[1]})
            table[key].append(scanpoint)

    return table


if __name__ == '__main__':

    import sys, json, pickle

    # read config file
    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    Luminometer = str(ConfigInfo['Luminometer'])
    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    OutputSubDir = AnalysisDir + "/" + str(ConfigInfo['OutputSubDir'])

    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     

    table = {}
    csvtable = []

    table = doMakeRateFile(ConfigInfo)

    with open(OutputSubDir+'/Rates_'+str(Luminometer)+'_'+str(Fill)+'.json', 'wb') as f:
        json.dump(table, f)
            





