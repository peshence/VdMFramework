import FitManager
import ROOT as r
import sys
import math
from vdmUtilities import *

class SGConst_Fit(FitManager.FitProvider):

    fitDescription = """ Single Gaussian with const background.
    ff = r.TF1("ff","[3] + [2]*exp(-(x-[1])**2/(2*[0]**2))")
    ff.SetParNames("#Sigma","Mean","peak","Const") """

    def __init__(self):

        self.table = []

        self.table.append(["Scan", "Type", "BCID", "sigma","sigmaErr", \
                      "Mean","MeanErr", "Const", "ConstErr", "CapSigma", "CapSigmaErr", "peak", "peakErr", \
                      "area", "areaErr","fitStatus", "chi2", "ndof", 'covStatus'])



    def doFit( self,graph,config):

        makeLogs = config['MakeLogs']

        # Making these presettable - to make any parameter a constant just
        # set the two limits the same value as the starting parameter
        ExpSigma = graph.GetRMS()*0.5 if config['LimitsSigma'][0] != config['StartSigma']\
                                        or config['LimitsSigma'][1] != config['StartSigma'] else 1
        ExpPeak = graph.GetHistogram().GetMaximum() if config['LimitsPeak'][0] != config['StartPeak']\
                                        or config['LimitsPeak'][1] != config['StartPeak'] else 1

        StartSigma = ExpSigma * config['StartSigma']
        LimitSigma_lower = config['LimitsSigma'][0]
        LimitSigma_upper = config['LimitsSigma'][1]

        StartPeak = ExpPeak * config['StartPeak']
        LimitPeak_lower = config['LimitsPeak'][0]
        LimitPeak_upper = config['LimitsPeak'][1]

        StartConst = config['StartConst']
        LimitConst_lower = config['LimitsConst'][0]
        LimitConst_upper = config['LimitsConst'][1]


        ff = r.TF1("ff","[3] + [2]*exp(-(x-[1])**2/(2*[0]**2))")
        ff.SetParNames("#Sigma","Mean","peak","Const")

        ff.SetParameters(StartSigma,0.,StartPeak, StartConst)

        if LimitSigma_upper > LimitSigma_lower:
            ff.SetParLimits(0, LimitSigma_lower,LimitSigma_upper)
        if LimitPeak_upper > LimitPeak_lower:
            ff.SetParLimits(2, LimitPeak_lower,LimitPeak_upper)
        if LimitConst_upper == LimitConst_lower:
            ff.FixParameter(3, StartConst)

        # Some black ROOT magic to get Minuit output into a log file
        # see http://root.cern.ch/phpBB3/viewtopic.php?f=14&t=14473,
        # http://root.cern.ch/phpBB3/viewtopic.php?f=13&t=16844,
        # https://agenda.infn.it/getFile.py/access?resId=1&materialId=slides&confId=4933 slide 23

        if makeLogs:
            r.gROOT.ProcessLine("gSystem->RedirectOutput(\"" + config['MinuitFile'] + "\", \"a\");")

        for j in range(5):
            fit = graph.Fit("ff","SV" if makeLogs else 'SQ')
            if fit.CovMatrixStatus()==3 and fit.Chi2()/fit.Ndf() < 2: break

        fitStatus = -999
        fitStatus = fit.Status()

        CapSigma = ff.GetParameter("#Sigma")
        m = ff.GetParNumber("#Sigma")
        CapSigmaErr = ff.GetParError(m)
        mean = ff.GetParameter("Mean")
        m = ff.GetParNumber("Mean")
        meanErr = ff.GetParError(m)
        peak = ff.GetParameter("peak")
        m = ff.GetParNumber("peak")
        peakErr = ff.GetParError(m)
        const = ff.GetParameter("Const")
        m = ff.GetParNumber("Const")
        constErr = ff.GetParError(m)


        title = graph.GetTitle()
        title_comps = title.split('_')
        scan = title_comps[0]
        type = title_comps[1]
        bcid = str(int(title_comps[2]))
        chi2 = ff.GetChisquare()
        ndof = ff.GetNDF()
        
        xmax = r.TMath.MaxElement(graph.GetN(),graph.GetX())

        sqrttwopi = math.sqrt(2*math.pi)
        
        if makeLogs:
            r.gROOT.ProcessLine("gSystem->Info(0,\"BCID " + bcid + " done\");")
            r.gROOT.ProcessLine("gSystem->RedirectOutput(0);")

        sigma = CapSigma/math.sqrt(2)
        sigmaErr = CapSigmaErr/math.sqrt(2)

        area  = sqrttwopi*peak*CapSigma
        areaErr = (sqrttwopi*CapSigma*peakErr)*(sqrttwopi*CapSigma*peakErr) +\
                  (sqrttwopi*peak*CapSigmaErr)*(sqrttwopi*peak*CapSigmaErr)
        areaErr = math.sqrt(areaErr)

        self.table.append([scan, type, bcid, sigma, sigmaErr, mean, meanErr, const, constErr,\
                           CapSigma, CapSigmaErr, peak, peakErr, area, areaErr, fitStatus, chi2,\
                           ndof, fit.CovMatrixStatus()])


        # Define signal and background pieces of full function separately, for plotting

        fSignal = r.TF1("fSignal","[2]*exp(-(x-[1])**2/(2*[0]**2))")
        fSignal.SetParNames("#Sigma","Mean","Amp")
        fSignal.SetParameters(CapSigma, mean, peak)

        import array
        errors = array.array('d',[CapSigmaErr, meanErr, peakErr])
        fSignal.SetParErrors(errors)

        fBckgrd =r.TF1("fBckgrd","[0]")
        fBckgrd.SetParNames("Const")
        const = ff.GetParameter("Const")
        m = ff.GetParNumber("Const")
        constErr = ff.GetParError(m)
        fBckgrd.SetParameter(0,const)
        fBckgrd.SetParError(0,constErr)

        functions = [ff, fSignal, fBckgrd]

        return [functions, fit]


    def doPlot(self, graph, functions, fill, tempPath):
        
        canvas =  r.TCanvas()
        canvas = doPlot1D(graph, functions, fill, tempPath)
        return canvas
