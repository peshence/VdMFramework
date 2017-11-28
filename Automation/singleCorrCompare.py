import os
import pandas as pd
import matplotlib.pyplot as plot
import numpy as np
from math import floor as floor
from math import log10 as log10
from matplotlib.font_manager import FontProperties

fontP = FontProperties()
fontP.set_size('small')

corrected = os.getcwd() + '/Analysed_Data/'
uncorrected = '/brildata/vdmoutput/Automation/Analysed_Data/'


goodnames = ['\sigma_{vis}','\Sigma_X','\Sigma_Y']
varnames = ['xsec','capx','capy']
detectors = ['PLT', 'HFET']

def main(dif):
    if dif and os.getcwd()[-1]=='0': return
    def plotfit(x,y,goodname):
        (la,lb), cov = np.polyfit(x, y, 1,cov=True)
        def round_to_sign(x):
            return round(x, -int(floor(log10(abs(x))))+1)
        lae = round_to_sign(cov[0][0])
        lbe = round_to_sign(cov[1][1])
        la = round(la,len(str(lae)) - '{0:f}'.format(lae).index('.') - 1)
        lb = round(lb,len(str(lbe)) - '{0:f}'.format(lbe).index('.') - 1)
        plot.plot(x, [la*i + lb for i in x], label = '(' + str(la) + '$\pm$' + str(lae) + ')x + ' + str(lb) + '$\pm$' + str(lbe))
        plot.ylabel(('$\Delta ' if dif else '$') + goodname + '$ [%]')
        plot.xlabel('SBIL')

    def do(goodname,detector,v):
        plot.close()
        fit = 'G' if detector == 'PLT' else 'GConst'
        leadx = []
        leady=[]
        trainx=[]
        trainy=[]
        c=1
        plot.rcParams["figure.figsize"] = (32, 18)

        for fol in os.listdir(corrected):
            f1 = fol + '/' + detector + '/results/BeamBeam/LumiCalibration_' + detector + '_S' + fit + '_' + fol[:4] +'.csv'
            f2 = fol + '/' + detector + '/results/BeamBeam/LumiCalibration_' + detector + '_D' + fit + '_' + fol[:4] +'.csv'
            f = f1 #if os.path.exists('Analysed_Data/' + f1) else f2

            lumicorr = pd.DataFrame.from_csv(corrected + f)
            lumi = pd.DataFrame.from_csv(uncorrected + f)
            f1 = fol + '/' + detector + '/results/BeamBeam/S' + fit + '_FitResults.csv'
            f2 = fol + '/' + detector + '/results/BeamBeam/D' + fit + '_FitResults.csv'
            f = f1 if os.path.exists('Analysed_Data/' + f1) else f2
            fitparamscorr = pd.DataFrame.from_csv(corrected + f)
            fitparams = pd.DataFrame.from_csv(uncorrected + f)
            def removesum(pds):
                fuckingindex = [True if i!='sum' else False for i in pds.BCID ]
                return pds.loc[fuckingindex,:]
            fitparams = removesum(fitparams)
            fitparamscorr = removesum(fitparamscorr)
            lumi = removesum(lumi)
            lumicorr = removesum(lumicorr)

            if not dif:
                xsec = [j/np.mean(lumicorr.xsec)*100 for i,j in zip(lumi.xsec, lumicorr.xsec)]
                capx = [j/np.mean(fitparamscorr.CapSigma[:len(lumi.xsec)])*100 for i,j in zip(fitparams.CapSigma[:len(lumi.xsec)], fitparamscorr.CapSigma[:len(lumi.xsec)])]
                capy = [j/np.mean(fitparamscorr.CapSigma[len(lumi.xsec):])*100 for i,j in zip(fitparams.CapSigma[len(lumi.xsec):], fitparamscorr.CapSigma[len(lumi.xsec):])]
            else:
                xsec = [(i-j)/i * 100 for i,j in zip(lumi.xsec, lumicorr.xsec)]
                capx = [(i-j)/i * 100 for i,j in zip(fitparams.CapSigma[:len(lumi.xsec)], fitparamscorr.CapSigma[:len(lumi.xsec)])]
                capy = [(i-j)/i * 100 for i,j in zip(fitparams.CapSigma[len(lumi.xsec):], fitparamscorr.CapSigma[len(lumi.xsec):])]
            
            dick = {'xsec':xsec, 'capx':capx, 'capy':capy, 'sbil':lumicorr.SBIL}
            print len(xsec), len(capx),len(capy),len(lumicorr.SBIL)
            df = pd.DataFrame.from_dict(dick)
            df = df.loc[:, ['sbil', 'capx', 'capy', 'xsec']]
            df.index = lumicorr.BCID 

            df.to_csv('SG_' + ('diff' if dif else '') + detector + '_' + fol + '.csv')
            fill = 'Fill ' + ('6362 Early scan' if fol =='6362_04Nov17_220358_04Nov17_220637' else '6362 Late scan' if fol == '6362_05Nov17_182035_05Nov17_182308' else fol[:4])
            lead = df.loc[[i for i in df.index if int(i)-1 not in df.index],:]
            train = df.loc[[i for i in df.index if int(i)-1 in df.index],:]
            def plotthishit(varname, goodname, coord):
                print coord
                plot.subplot(coord)
                plot.plot(lead.sbil,lead.loc[:,varname],'o',label='lead')
                plot.plot(train.sbil,train.loc[:,varname],'o',label='train')
                plotfit(lead.sbil,lead.loc[:,varname],goodname)
                if not train.sbil.empty:
                    plotfit(train.sbil,train.loc[:,varname],goodname)        
                plot.legend(prop=fontP)
                plot.title(detector + ' effect of nonlinearity on ' + ('$\Delta ' if dif else '$') + goodname + '$ \n' + fill)
                
            plotthishit(v,goodname,240 + c)
            leadx = leadx + lead.sbil.tolist()
            leady = leady + lead.loc[:,v].tolist()
            trainx = trainx + train.sbil.tolist()
            trainy = trainy + train.loc[:,v].tolist()
            
            c = c+1 if int(c)%4 == 1 else c+3
            

        # plotthishit('xsec','\sigma_{vis}',122)
        plot.subplot(122)
        plot.plot(leadx,leady,'o',label='lead')
        plot.plot(trainx,trainy,'o',label='train')
        plotfit(leadx,leady,goodname)
        plotfit(trainx,trainy,goodname)
        plot.ylabel(('$\Delta ' if dif else '$') + goodname + '$ [%]')
        plot.xlabel('SBIL')
        plot.title(detector + ' effect of nonlinearity on ' + ('$\Delta ' if dif else '$') + goodname + '$ \nAll 4 scans')
        plot.legend()
        # plotthishit('capx','\Sigma_X',323)
        # plotthishit('capy','\Sigma_Y',325)

        plot.savefig('SG_' + ('diff_' if dif else '') + detector + '_' + v + '.png')
        # plot.show()
        
    for d in detectors:
        for g,v in zip(goodnames,varnames):
            do(g,d,v)


main(False)
main(True)