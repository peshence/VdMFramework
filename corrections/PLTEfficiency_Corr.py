import CorrectionManager
import pickle
import vdmUtilities
import fitResultReader()

class PLTEfficiency_Corr(CorrectionManager.CorrectionProvider):

    def doCorr(self,inData,configFile):

        lumiCalibrationFile = configFile['inputSBIL']
        lumicalibration = pd.DataFrame.from_csv(lumiCalibrationFile)
        sbil = {}
        for i in lumicalibration.iterrows():
            sbil.update({i[1]['BCID']:i[1]['SBIL']})
        sbil = [{i['BCID''SBIL'] for i in lumicalibration]

        for entry in inData:
            scanNumber = entry.scanNumber
            key = "Scan_"+str(scanNumber)
            for i, bx in enumerate(entry.collidingBunches):


        

