import CorrectionManager
import json
import numpy as np

class Background_Corr(CorrectionManager.CorrectionProvider):
    '''
    Correction substracts a constant estimated background accounting for MIB and noise as estimated
    from filled non-colliding bunches and abort gap (last 120 bunches) respectively
    '''
    def doCorr(self, inData, filename):
        '''
        Subtracts a constant background from rates in inData according to Background file 
        with a background ('background') and an error ('backgroundError')
        '''
        print filename
        with open(filename) as f:
            d = json.load(f)
        background, background_err = d['background'], d['backgroundError']
        for entry in inData:
            scanNumber = entry.scanNumber
            key = "Scan_"+str(scanNumber)
            lumi = []
            for bx in entry.lumi:
                lumi.append([i - background for i in bx])
            entry.lumi = lumi

            lumiErr = []
            for bx in entry.lumiErr:
                lumiErr.append([np.sqrt(i**2 + background_err**2) for i in bx])
            entry.lumiErr = lumiErr


