import tables as t
import json
import numpy as np

class BeamBeam_Corr(CorrectionManager.CorrectionProvider):
    def removestrays(a):
        return np.array([False if i < 6e9 else True for i in a])

    def doCorr(self, inData, filename, rateTable):
        with t.open_file(filename) as hd5:
            for r in hd5.root.beam:
                bunchlist1 = removestrays(r['bxintensity1'])
                bunchlist2 = removestrays(r['bxintensity2'])

                fillednoncolliding = (bunchlist1 | bunchlist2) & ~(bunchlist1 & bunchlist2)
                break

            for table in hd5.root:
                    if table.name == rateTable:
                        beamtable = table
                        break
            
            backgrounds = []
            for r in beamtable:
                backgrounds.append(np.mean(r['bxraw'][fillednoncolliding]))
            background = np.mean(backgrounds)

            for entry in inData:
                scanNumber = entry.scanNumber
                key = "Scan_"+str(scanNumber)

                for i in entry.spPerBX:
                    i = i - background


