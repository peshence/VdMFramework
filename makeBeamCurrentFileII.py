import ROOT
import tables
import numpy as np
from scipy import stats
import pandas as pd

import json
import os

def sumCurrents(curr, bcidList):

    sumCurr = 0.0
    if curr:
        for bcid in bcidList:
            sumCurr = sumCurr + curr[str(bcid)]
    else: 
        print "Attention: No beam currents for time period of scan found in input files"
    
    return sumCurr


def checkFBCTcalib(table, CalibrateFBCTtoDCCT):

    h_ratioB1 = ROOT.TGraph()
    h_ratioB1.SetMarkerStyle(8)
    h_ratioB1.SetMarkerSize(0.4)
    h_ratioB1.SetTitle("SumFBCT/DCCT for B1, for scan "+str(table[0][1]))
    h_ratioB1.GetXaxis().SetTitle("Scan point number")
    h_ratioB1.GetYaxis().SetTitle("SumFBCT(active bunches)/DCCT")

    h_ratioB2 = ROOT.TGraph()
    h_ratioB2.SetMarkerStyle(8)
    h_ratioB2.SetMarkerSize(0.4)
    h_ratioB2.SetTitle("SumFBCT/DCCT for B2, for scan "+str(table[0][1]))
    h_ratioB2.GetXaxis().SetTitle("Scan point number")
    h_ratioB2.GetYaxis().SetTitle("SumFBCT(active bunches)/DCCT")


    for idx, entry in enumerate(table):
        h_ratioB1.SetPoint(idx, entry[2], entry[5]/entry[3])
        h_ratioB2.SetPoint(idx, entry[2], entry[6]/entry[4])


    h_ratioB1.Fit("pol0")
    h_ratioB2.Fit("pol0")

    fB1 = ROOT.TF1()
    fB2 = ROOT.TF1()
    fB1 = h_ratioB1.GetFunction("pol0")
    fB2 = h_ratioB2.GetFunction("pol0")

    corrB1 = fB1.GetParameter(0)
    corrB2 = fB2.GetParameter(0)

    if CalibrateFBCTtoDCCT == True:
        print "Applying FBCT to DCCT calibration"

        for idx, entry in enumerate(table):
            #K1=entry[5]/entry[3]
            #K2=entry[6]/entry[4]
            for key in entry[7].keys():
                old1 = entry[7][key]
                #entry[7][key] = old1/K1
                entry[7][key] = old1/corrB1
            for key in entry[8].keys():
                old2 =  entry[8][key]
                #entry[8][key] = old2/K2
                entry[8][key] = old2/corrB2

            old1=entry[5]
            #entry[5]=old1/K1
            entry[5]=old1/corrB1
            old2=entry[6]
            #entry[6]=old2/K2
            entry[6]=old2/corrB2

    return [h_ratioB1, h_ratioB2, table]

def getCurrents(datapath, scanpt, fill):

    beamts = []
    bx1data = []
    bx2data = []
    bx1df = pd.DataFrame()
    bx2df = pd.DataFrame()

    beam1data = []
    beam2data = [] 
    beam1df = pd.DataFrame()
    beam2df = pd.DataFrame()

    fbct1 = {}
    fbct2 = {}

    dcct1 = 0.0
    dcct2 = 0.0

    filledBunches1 = []
    filledBunches2 = []
    collBunches=[]

    # omit very first nibble because it may not be fully contained in VdM scan
    tw = '(timestampsec >' + str(scanpt[0]) + ') & (timestampsec <=' +  str(scanpt[1]) + ')'
    print "tw", tw

    def readh5(filename, collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data, beamts):
        with tables.open_file(filename, 'r') as h5file:
            # if not file or len(file) < 25 or h5file.root.beam[-1]['timestampsec'] < scanpt[0] or h5file.root.beam[0]['timestampsec'] > scanpt[1]:
            #     h5file.close()
            #     continue
            beamtable = [(r['bxintensity1'], r['bxintensity2'], r['timestampsec'], r['intensity1'], r['intensity2']) for r in h5file.root.beam.where(tw)]
            
            removestrays = lambda a: np.array([0 if i < 6e9 else 1 for i in a])
            bunchlist1 = [removestrays(r[0]) for r in beamtable] 
            bunchlist2 = [removestrays(r[1]) for r in beamtable]        
            beamtslist = [r[2] for r in beamtable]
            beamts = beamts + beamtslist

            if bunchlist1 and bunchlist2:
                collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
                filledBunches1 = np.nonzero(bunchlist1[0])[0].tolist()
                filledBunches2 = np.nonzero(bunchlist2[0])[0].tolist()

                # dcct, i.e. current per beam
                beam1list = [r[3] for r in beamtable]
                beam2list = [r[4] for r in beamtable]
                beam1data = beam1data + beam1list
                beam2data = beam2data + beam2list
                # fbct, ie. current per bx 
                bx1list = [r[0] for r in beamtable]
                bx2list = [r[1] for r in beamtable]
                # only consider nominally filled bunches
                bx1data = bx1data + (bx1list* bunchlist1[0]).tolist()
                bx2data = bx2data + (bx2list* bunchlist2[0]).tolist()
        return collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data,beamts
    
    if datapath[-4:] == '.hd5':
        collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data,beamts = readh5(datapath, collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data,beamts)
    else:        
        filelist = os.listdir(datapath)
        for file in filelist:
            if str.isdigit(str(file[0])) and int(file[:4]) == int(fill):
                collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data,beamts = readh5(datapath + '/' + file, collBunches, filledBunches1, filledBunches2, beam1data, beam2data, bx1data, bx2data,beamts)        

    beam1df = pd.DataFrame(beam1data)
    beam2df = pd.DataFrame(beam2data)
    
    bx1df = pd.DataFrame(bx1data)
    bx2df = pd.DataFrame(bx2data)

    if beam1df.empty or beam2df.empty or bx1df.empty or bx2df.empty:
        print "Attention, beam current df empty because timestamp window not contained in file"
    else:
        dcct1 = float(beam1df.mean())
        dcct2 = float(beam2df.mean())

    # attention: LHC bcid's start at 1, not at 0

        ## In 4266 BCID 2674 is 3% too low in FBCT
        if fill == 4266:

            for idx, bcid in enumerate(filledBunches1):
                if bcid+1==2674:
                    fbct1[str(bcid+1)] = 1.03*bx1df[bcid].mean()
                else:
                    fbct1[str(bcid+1)] = bx1df[bcid].mean()

            for idx, bcid in enumerate(filledBunches2):
                if bcid+1==2674:
                    fbct2[str(bcid+1)] = 1.03*bx2df[bcid].mean()
                else:
                    fbct2[str(bcid+1)] = bx2df[bcid].mean()

        ## In 4634 even BCIDs are 4% too high in FBCT
        elif fill == 4634:

            for idx, bcid in enumerate(filledBunches1):
                if (bcid+1)%2 == 0:
                    fbct1[str(bcid+1)] = 1.04*bx1df[bcid].mean()
                else:
                    fbct1[str(bcid+1)] = bx1df[bcid].mean()

            for idx, bcid in enumerate(filledBunches2):
                fbct2[str(bcid+1)] = bx2df[bcid].mean()

        else:

            for idx, bcid in enumerate(filledBunches1):
                fbct1[str(bcid+1)] = bx1df[bcid].mean()

            for idx, bcid in enumerate(filledBunches2):
                fbct2[str(bcid+1)] = bx2df[bcid].mean()

        for idx, bcid in enumerate(filledBunches1):
            old=filledBunches1[idx]
            filledBunches1[idx]=old+1

        for idx, bcid in enumerate(filledBunches2):
            old=filledBunches2[idx]
            filledBunches2[idx]=old+1

        for idx, bcid in enumerate(collBunches):
            old=collBunches[idx]
            collBunches[idx]=old+1

    return dcct1, dcct2, fbct1, fbct2, filledBunches1, filledBunches2, collBunches

############################
def doMakeBeamCurrentFile(ConfigInfo):

    import csv, pickle

    AnalysisDir = str(ConfigInfo['AnalysisDir'])
    InputCentralPath = str(ConfigInfo['InputCentralPath'])
    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    OutputSubDir = str(ConfigInfo['OutputSubDir'])

    outpath = './' + AnalysisDir + '/' + OutputSubDir 

    CalibrateFBCTtoDCCT = False
    CalibrateFBCTtoDCCT = ConfigInfo['CalibrateFBCTtoDCCT']

    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     
    ScanNames = scanInfo["ScanNames"]     

    table = {}
    csvtable = []
#    csvtable.append(["ScanNumber, ScanNames, ScanPointNumber, avrgdcct1, avrgdcct2, sum(avrgfbctB1), sum(avrgfbctB2), sumColl(avrgfbct1), sumColl(avrgfbct2), fbct1 per Bx, fbct2 per BX"])
    csvtable.append(["ScanNumber, ScanNames, ScanPointNumber, avrgdcct1, avrgdcct2, sum(avrgfbctB1), sum(avrgfbctB2), fbct1 per Bx, fbct2 per BX"])

    for i in range(len(ScanNames)):
        key = "Scan_" + str(i+1)
        scanpoints = scanInfo[key]
        table["Scan_" + str(i+1)]=[]
        for j, sp in enumerate(scanpoints):
            avrgdcct1, avrgdcct2, avrgfbct1, avrgfbct2, FilledBunchesB1, FilledBunchesB2, CollidingBunches = getCurrents(InputCentralPath, sp[3:], int(Fill))

#Sums over all filled bunches
            sumavrgfbct1 = sumCurrents(avrgfbct1, FilledBunchesB1) 
            sumavrgfbct2 = sumCurrents(avrgfbct2, FilledBunchesB2)
#Sums over all colliding bunches
            sumCollavrgfbct1 = sumCurrents(avrgfbct1, CollidingBunches) 
            sumCollavrgfbct2 = sumCurrents(avrgfbct2, CollidingBunches) 
            avrgfbct1['sum'] = sumCollavrgfbct1
            avrgfbct2['sum'] = sumCollavrgfbct2

            print "Scan point", j, sp
            row = [i+1, str(ScanNames[i]), j+1, avrgdcct1, avrgdcct2, sumavrgfbct1, sumavrgfbct2, avrgfbct1, avrgfbct2]
            table["Scan_" + str(i+1)].append(row)

    canvas = ROOT.TCanvas()

    ROOT.gStyle.SetOptFit(111)
    ROOT.gStyle.SetOptStat(0)

    h_ratioB1 = ROOT.TGraph()
    h_ratioB2 = ROOT.TGraph()

    outpdf = outpath+'/checkFBCTcalib_'+str(Fill)+'.pdf'
    for i in range(len(ScanNames)):
        key = "Scan_" + str(i+1)
        [h_ratioB1, h_ratioB2, table[key]] = checkFBCTcalib(table[key], CalibrateFBCTtoDCCT)
        h_ratioB1.Draw("AP")
        canvas.SaveAs(outpdf + '(')
        h_ratioB2.Draw("AP")
        canvas.SaveAs(outpdf + '(')

    canvas.SaveAs(outpdf + ']')

    for i in range(len(ScanNames)):
        key="Scan_"+str(i+1)
        csvtable.append([str(key)])
        for idx, entry in enumerate(table[key]):
            row=[entry[0],entry[1],entry[2],entry[3],entry[4],entry[5],entry[6],entry[7],entry[8]]
            csvtable.append(row)

    return table, csvtable

##############
if __name__ == '__main__':

    import pickle, csv, sys, json

    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    AnalysisDir = str(ConfigInfo["AnalysisDir"])
    OutputSubDir = str(ConfigInfo["OutputSubDir"])


    InputScanFile = './' + AnalysisDir + '/' + str(ConfigInfo['InputScanFile'])
    with open(InputScanFile, 'rb') as f:
        scanInfo = pickle.load(f)

    Fill = scanInfo["Fill"]     

    table = {}
    csvtable = []

    table, csvtable = doMakeBeamCurrentFile(ConfigInfo)
    
    outpath = AnalysisDir + '/' + OutputSubDir

    csvfile = open(outpath+'/BeamCurrents_'+str(Fill)+'.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerows(csvtable)
    csvfile.close()

    with open(outpath+'/BeamCurrents_'+str(Fill)+'.pkl', 'wb') as f:
        pickle.dump(table, f)
            
