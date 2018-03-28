import CorrectionManager
import ROOT as r
import sys
import os
import json
from vdmUtilities import *

class BeamBeam_Corr(CorrectionManager.CorrectionProvider):

    BBcorr = {}

    def GetCorr(self, fileName):

        table = {}
        with open(fileName, 'rb') as f:
            table = json.load(f)

        self.BBcorr = table 

        return


    def PrintCorr(self):

        print ""
        print "===="
        print "PrintBeamBeamCorr"
        print "Correction factors derived from fits to uncorrected distributions"
        print "Correction factors depend on scan number, scan point number and bcid"
        print "===="
        print ""


    def doCorr(self,inData,configFile,makepdf):

        print "Correcting coordinates with beambeam correction factors"

        self.GetCorr(configFile)
        
        self.PrintCorr()

        #put pdf in file with same location and name as correction file, just with ending pdf instead of pkl
        pdfName = configFile[:configFile.index(".json")] + ".pdf"
        canvas = r.TCanvas()
        canvas.SetGrid()
        # buffer for log file                    
        logbuffer="The list of bunches with incomplete scanpoint lists. These BCIDs are excluded when BeamBeam is applied.\n"

        # apply correction here to coordinate, then write back into entry, check if this really changes value in calling function

        for entry in inData:
            scanNumber = entry.scanNumber
            key = "Scan_"+str(scanNumber)

            corrPerSP  = self.BBcorr[key]        

            corrXPerSP = [{} for value in corrPerSP]
            corrYPerSP = [{} for value in corrPerSP]
            for value in corrPerSP:
                corrXPerSP[value['ScanPointNumber']-1] = value['corr_Xcoord']
                corrYPerSP[value['ScanPointNumber']-1] = value['corr_Ycoord']
            
            logbuffer=logbuffer+key+"\n"
            exclBXList=[]
    
            corrXPerBX = {bx:[] for bx in entry.collidingBunches}
            corrYPerBX = {bx:[] for bx in entry.collidingBunches}
            BB_bxList=[]
            for i, bx in enumerate(entry.collidingBunches):
                try:
                    for j in range(entry.nSP):
                        valueX = corrXPerSP[j][str(bx)]
                        corrXPerBX[bx].append(valueX)
                        valueY = corrYPerSP[j][str(bx)]
                        corrYPerBX[bx].append(valueY)
                except:
                    print bx," is missing; don't fill corr per bx"
                    exclBXList.append(bx)
                else:
                    BB_bxList.append(bx)
            #BB_bxList=corrXPerBX.keys()

            for index in BB_bxList:
                if 'X' in entry.scanName:
                    entry.spPerBX[index] = [a+b for a,b in zip(entry.spPerBX[index], corrXPerBX[index])]
                if 'Y' in entry.scanName:
                    entry.spPerBX[index] = [a+b for a,b in zip(entry.spPerBX[index], corrYPerBX[index])]                    

            entry.usedCollidingBunches=BB_bxList

            #for bx in entry.collidingBunches:
            pdfbxs = [i for i in BB_bxList if type(i) == int][:100]
            pdfbxs = pdfbxs + [key for key in BB_bxList if type(i) == int and key not in pdfbxs and
                            key - 1 not in BB_bxList and key + 1 not in BB_bxList]
            for bx in pdfbxs:
                histo = r.TGraph()
                histo.SetMarkerStyle(8)
                histo.SetMarkerSize(0.4)
                try:
                    for j in range(entry.nSP):
                        hidx = entry.scanName + "_"+str(bx)
                        htitle= "BeamBeam correction for " + str(hidx)
                        if 'X' in entry.scanName:
                            histo.SetPoint(j,entry.spPerBX[bx][j],corrXPerBX[bx][j]) 
                            histo.SetTitle(htitle)
                        if 'Y' in entry.scanName:
                            histo.SetPoint(j,entry.spPerBX[bx][j],corrYPerBX[bx][j]) 
                            histo.SetTitle(htitle)
                    histo.Draw("AP")
                    histo.GetXaxis().SetTitle('nominal displacement in mm')
                    histo.GetYaxis().SetTitle('correction from beam-beam in mm')
                    if makepdf:
                        canvas.SaveAs(pdfName+'(')
                except:
                    print bx," is missing; no BeamBeam corr."

            logbuffer=logbuffer+str(exclBXList)+"\n"

        if makepdf:
            canvas.SaveAs(pdfName + ']')
        
        logName = configFile[:configFile.index(".json")] + ".log"                
        excldata=open(logName,'w')
        excldata.write(logbuffer)
        excldata.close()

