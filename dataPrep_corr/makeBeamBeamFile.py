import sys, json, csv
from inputDataReaderII import *
import numpy as np
from numpy import sqrt, pi, exp,sign

from BB import BB

# calls python script written by T. Pieloni and W. Kozanecki
# needs shared library errffor.so
# to make shared library:
# f2py --opt="-O3" -c -m errffor --fcompiler=gfortran  --link-lapack_opt *.f
# This works under anaconda python, with ROOT version linked against anaconda python, see env_anaconda.py

def doMakeBeamBeamFile(ConfigInfo):


    AnalysisDir = ConfigInfo['AnalysisDir']
    Luminometer = ConfigInfo['Luminometer']
    InputScanFile = ConfigInfo['InputScanFile']
    InputBeamCurrentFile = ConfigInfo['InputBeamCurrentFile']
    inputLuminometerData = str(ConfigInfo['InputLuminometerData'])
    InputCapSigmaFile = AnalysisDir + '/' + Luminometer + '/results/' + ConfigInfo['InputCapSigmaFile']
    Scanpairs = ConfigInfo['Scanpairs']

    inData1 = vdmInputData(1)
    inData1.GetScanInfo(AnalysisDir + '/'+ InputScanFile)
    inData1.GetBeamCurrentsInfo(AnalysisDir + '/' + InputBeamCurrentFile)
    inData1.GetLuminometerData(AnalysisDir + '/' + inputLuminometerData)

    Fill = inData1.fill
    
    inData = []
    inData.append(inData1)

    # For the remaining scans:

    for i in range(1,len(inData1.scanNamesAll)):
        inDataNext = vdmInputData(i+1)
        inDataNext.GetScanInfo(AnalysisDir + '/' + InputScanFile)
        inDataNext.GetBeamCurrentsInfo(AnalysisDir + '/' + InputBeamCurrentFile)
        inDataNext.GetLuminometerData(AnalysisDir + '/' + inputLuminometerData)
        inData.append(inDataNext)

    from collections import defaultdict
    CapSigma = defaultdict(dict)
    
    from fitResultReader import *
    fitResult = fitResultReader(InputCapSigmaFile)
    CapSigma = fitResult.getFitParam("CapSigma")

    ## input to BB:
    ## CapSigma's must be in microns
    for entry in CapSigma:
        for param in CapSigma[entry]:
            value = CapSigma[entry][param]
            value =  value * 1000
            CapSigma[entry][param] = value 


    # Separations must be in mm
    # LHC tunes (units: 2*pi)
    # taken from BBscan.py macro provided by T. Pieloni and W. Kozanecki
    tunex = 64.31
    tuney = 59.32

    # for output
    table = {}

    # figure out which scans to consider as pair
    for entry in Scanpairs:
            scanx = entry[0]
            scany = entry[1]

            # Counting of scans starts with 1, index in inData starts with 0

            inDataX = inData[scanx-1]
            inDataY = inData[scany-1]

            keyx = "Scan_"+ str(scanx)
            keyy = "Scan_"+ str(scany)

            table[keyx] = []
            table[keyy] = []

            CsigxList = CapSigma[keyx]
            CsigyList = CapSigma[keyy] 

            # IP beta functions beta* of deflected bunch (units: m; INPUT IN METERS)
            betax = float(inDataX.betaStar)
            betay = float(inDataY.betaStar)

        # <<<<<>>>>> For X scan:

            sepxList = inDataX.displacement
            sepyList = [0.0 for i in range(len(sepxList))]

            # for output
            orbitCorrX_xcoord = [{} for i in range(len(sepxList))]
            orbitCorrX_ycoord = [{} for i in range(len(sepyList))]

            # Attention: In the pPb and Pbp scans, one uses the proton-equivalent beam energy
            # beam energy in eV
            Ep1 = inDataX.energyB1
            Ep1 = float(Ep1)*1e9
            Ep2 = inDataX.energyB2
            Ep2 = float(Ep2)*1e9

            # Np = intensity of opposite beam in number of protons per bunch
            NpList1 = inDataX.avrgFbctB2PerSP
            NpList2 = inDataX.avrgFbctB1PerSP
            
            for bx in inDataX.usedCollidingBunches:
                lengthX=len(inDataX.spPerBX[bx])
                #print "bx=", bx, " lengthX=", lengthX, " sepxList=", len(sepxList), " lengthY=", len(inDataY.spPerBX[bx])
                if(lengthX==len(sepxList)):
                    # try:
                        lengthY=len(inDataY.spPerBX[bx])
                        if(lengthY==len(inDataY.displacement)):
                            Csigx = CsigxList[str(bx)]
                            Csigy = CsigyList[str(bx)]
                            for i in range(len(sepxList)):
                                sepx= sepxList[i]
                                sepy= sepyList[i]
                                Np1 = NpList1[i][str(bx)]               
                                Np2 = NpList2[i][str(bx)]

                                # >>> Effect of beam2 on beam1:
                                # sepx and sepy are in mm, deltaOrbitX and deltaOrbitY are in microns
                                deflectionXB1, deflectionYB1, deltaOrbitXB1, deltaOrbitYB1 = BB(Csigx,Csigy,sepx,sepy,betax,betay,tunex,tuney,Np1, Ep1)

                                # >>> Effect of beam1 on beam2:
                                deflectionXB2, deflectionYB2, deltaOrbitXB2, deltaOrbitYB2 = BB(Csigx,Csigy,sepx,sepy,betax,betay,tunex,tuney,Np2, Ep2)

                                # turn orbitCorr into mm

                                orbitCorrX_xcoord[i][str(bx)] = (deltaOrbitXB1+deltaOrbitXB2)*1e-3
                                orbitCorrX_ycoord[i][str(bx)] = 0.0

                    # except KeyError:
                    #     print "From makeBeambeamFile.py: bx = ", bx, "does not exist in CsigyList"
                        

            for i in range(len(sepxList)):
                ##["ScanNumber, ScanName, ScanPointNumber, corr_Xcoord in mm per BX, corr_Ycoord in mm per BX"]
                row = {'ScanNumber':scanx,
                       'ScanName':"X"+str(scanx),
                       'ScanPointNumber':i+1,
                       'corr_Xcoord':orbitCorrX_xcoord[i],
                       'corr_Ycoord':orbitCorrX_ycoord[i]}
                table[keyx].append(row)
                            
        # <<<<<>>>>> For Y scan:

            sepyList = inDataY.displacement
            sepxList = [0.0 for i in range(len(sepyList))]

            # for output
            orbitCorrY_xcoord = [{} for i in range(len(sepxList))]
            orbitCorrY_ycoord = [{} for i in range(len(sepyList))]

            # Attention: In the pPb and Pbp scans, one uses the proton-equivalent beam energy
            # beam energy in eV
            Ep1 = inDataY.energyB1
            Ep1 = float(Ep1)*1e9
            Ep2 = inDataY.energyB2
            Ep2 = float(Ep2)*1e9

            # Np = intensity of opposite beam in number of protons per bunch
            NpList1 = inDataY.avrgFbctB2PerSP
            NpList2 = inDataY.avrgFbctB1PerSP

            for bx in inDataY.usedCollidingBunches:
                lengthY=len(inDataY.spPerBX[bx])
                if(lengthY==len(sepyList)):
                    try:
                        lengthX=len(inDataX.spPerBX[bx])
                        if(lengthX==len(inDataX.displacement)):
                            Csigx = CsigxList[str(bx)]
                            Csigy = CsigyList[str(bx)]
                            for i in range(len(sepyList)):
                                sepx= sepxList[i]
                                sepy= sepyList[i]
                                Np1 = NpList1[i][str(bx)]               
                                Np2 = NpList2[i][str(bx)]

                                # print ">>>"
                                # print Csigx, Csigy, sepx, sepy, betax,betay, tunex, tuney, Np2, Ep2

                                # >>> Effect of beam2 on beam1:
                                # sepx and sepy are in mm, deltaOrbitX and deltaOrbitY are in microns
                                deflectionXB1, deflectionYB1, deltaOrbitXB1, deltaOrbitYB1 = BB(Csigx,Csigy,sepx,sepy,betax,betay,tunex,tuney,Np1, Ep1)

                                # >>> Effect of beam1 on beam2:
                                deflectionXB2, deflectionYB2, deltaOrbitXB2, deltaOrbitYB2 = BB(Csigx,Csigy,sepx,sepy,betax,betay,tunex,tuney,Np2, Ep2)

                                # turn orbitCorr into mm
                                orbitCorrY_ycoord[i][str(bx)] = (deltaOrbitYB1+deltaOrbitYB2)*1e-3
                                orbitCorrY_xcoord[i][str(bx)] = 0.0

                    except KeyError:
                        print "From makeBeambeamFile.py: bx = ", bx, "does not exist in CsigxList" 
            for i in range(len(sepxList)):
                ##["ScanNumber, ScanName, ScanPointNumber, corr_Xcoord in mm per BX, corr_Ycoord in mm per BX"]
                row = {'ScanNumber':scany,
                       'ScanName':"Y"+str(scany),
                       'ScanPointNumber':i+1,
                       'corr_Xcoord':orbitCorrY_xcoord[i],
                       'corr_Ycoord':orbitCorrY_ycoord[i]}
                table[keyy].append(row)
    return table



if __name__ == '__main__':

    # read config file
    ConfigFile = sys.argv[1]

    Config=open(ConfigFile)
    ConfigInfo = json.load(Config)
    Config.close()

    Fill = ConfigInfo["Fill"]
    AnalysisDir = ConfigInfo["AnalysisDir"]
    Luminometer = ConfigInfo["Luminometer"]
    OutputDir = AnalysisDir +'/'+ConfigInfo["OutputSubDir"]

    table = {}
    table = doMakeBeamBeamFile(ConfigInfo)

    with open(OutputDir+'/BeamBeam_'+ Luminometer + '_' +str(Fill)+'.json', 'wb') as f:
        json.dump(table, f)


 
