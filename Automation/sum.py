import pandas as pd
import os
import re
import matplotlib.pyplot as plot
import matplotlib.gridspec as gridspec
import argparse
import numpy as np

detector = 'PLT'
fit = 'G' if detector == 'PLT' else 'GConst'
if not os.path.exists(detector):
    os.mkdir(detector)

parser = argparse.ArgumentParser()
parser.add_argument('-ft','--fulltrain', action='store_true')
parser.add_argument('-b4','--eb4e', action='store_true')
args=parser.parse_args()

dirs = os.listdir('Analysed_Data/')
pattern = re.compile('(.*)_[.^_]*')
scans = list(set([re.match(pattern,i).group(1) for i in dirs]))
only8b4e = args.eb4e
onlyFullTrains = args.fulltrain

globalSlope = {}

for scan in scans:
    plot.close()
    if (onlyFullTrains or only8b4e) and scan[:4] != '6194': continue
    # plot.rcParams["figure.figsize"] = (32, 18)
    # if scan[:4]=='6362':continue
    xsecs = {}
    capsigmasx = {}
    capsigmasy = {}

    sbils = {}

    for d in dirs:
        if scan not in d: continue
        f1 = 'Analysed_Data/' + d + '/' + detector + '/results/BeamBeam/LumiCalibration_' + detector + '_S' + fit + '_' + d[:4] +'.csv'
        f2 = 'Analysed_Data/' + d + '/' + detector + '/results/BeamBeam/LumiCalibration_' + detector + '_D' + fit + '_' + d[:4] +'.csv'
        f = f1 if os.path.exists(f1) else f2
        curxs = pd.DataFrame.from_csv(f)
        f1 = 'Analysed_Data/' + d + '/' + detector + '/results/BeamBeam/S' + fit + '_FitResults.csv'
        f2 = 'Analysed_Data/' + d + '/' + detector + '/results/BeamBeam/D' + fit + '_FitResults.csv'
        f = f1 if os.path.exists(f1) else f2
        cur = pd.DataFrame.from_csv(f)
        i = int(str(d[-1]))
        i = -1 * i if d[-2] == '-' else i
        capsigmasx.update({str(i):cur.CapSigma[:len(cur.CapSigma)/2]})
        capsigmasy.update({str(i):cur.CapSigma[len(cur.CapSigma)/2:]})
        xsecs.update({str(i):curxs.xsec})
        if i == 0:
            capsigmasx.update({'sbil':curxs.SBIL.tolist()})
            capsigmasy.update({'sbil':curxs.SBIL.tolist()})
            xsecs.update({'sbil':curxs.SBIL.tolist()})

    for k in capsigmasx.keys():
        if k == 'sbil': continue
        capsigmasx.update({k+'_diff':[(i-j)*100/j for i,j in zip(capsigmasx[k],capsigmasx['0'])]})
        capsigmasy.update({k+'_diff':[(i-j)*100/j for i,j in zip(capsigmasy[k],capsigmasy['0'])]})
        xsecs.update({k+'_diff':[(i-j)*100/j for i,j in zip(xsecs[k],xsecs['0'])]})


    csvname = ('8b4e ' + scan) if only8b4e else ('fulltrain ' + scan) if onlyFullTrains else scan
    def DataFrame(data, varname):
        tdf = pd.DataFrame.from_dict(data)
        cols = ['sbil','-5','-4','-3','-2','-1','0','1','2','3','4','5','-5_diff','-4_diff','-3_diff','-2_diff','-1_diff','0_diff','1_diff','2_diff','3_diff','4_diff','5_diff']
        tdf = tdf.loc[:,cols]
        tdf.index = curxs.BCID
        tdf['slope'] = [np.polyfit(range(-5,6),row[1][12:],1)[0] for row in tdf.iterrows()]
        tdf.to_csv(detector + '/' + csvname + '_' + varname + '.csv')
        return tdf
    dfx = DataFrame(capsigmasx,'capx')
    dfy = DataFrame(capsigmasy,'capy')
    df = DataFrame(xsecs,'xsec')

    fig = plot.figure(figsize=(32,18))
    grid = gridspec.GridSpec(3,1)
    fill = 'Fill ' + ('6362 Early scan' if scan =='6362_04Nov17_220358_04Nov17_220637' else '6362 Late scan' if scan == '6362_05Nov17_182035_05Nov17_182308' else scan[:4])
    fill = ('8b4e ' + fill) if only8b4e else ('fulltrain ' + fill) if onlyFullTrains else fill
    title = 'Effect of ' + detector + ' nonlinearity correction on $\sigma_{vis}$ and $\Sigma$ \n' + fill
    fig.suptitle(title,fontsize=24)
    
    i=0
    xsecplot = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=grid[0])
    capxplot = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=grid[1])
    capyplot = gridspec.GridSpecFromSubplotSpec(1,3,subplot_spec=grid[2])
    
    def plotVar(plt,df,varname,corrange):
        leadplot = plot.Subplot(fig,plt[0])
        leadplot.set_title(varname + ' leading bunches',fontsize=20)
        trainplot = plot.Subplot(fig,plt[1])
        trainplot.set_title(varname + ' train bunches',fontsize=20)
        sloplot = plot.Subplot(fig,plt[2])
        sloplot.set_title(varname + ' slopes vs SBIL',fontsize=20)
        lslope = []
        tslope = []
        lslopex = []
        tslopex = []
        for row in df.iterrows():
            if row[0]=='sum' or (only8b4e and int(row[0])<1000) or (onlyFullTrains and int(row[0])>1000): continue
            if str(int(row[0])-1) in df.index:
                trainplot.plot(corrange,row[1][12:-1])
                tslope.append(row[1][-1])
                tslopex.append(row[1][0])
            else:
                leadplot.plot(range(-5,6),row[1][12:-1])
                lslope.append(row[1][-1])
                lslopex.append(row[1][0])
        if varname in globalSlope.keys():
            globalSlope[varname]['x'] = globalSlope[varname]['x'] + tslopex + lslopex
            globalSlope[varname]['y'] = globalSlope[varname]['y'] + tslope + lslope
        else:
            globalSlope[varname] = {}
            globalSlope[varname]['x'] = tslopex + lslopex
            globalSlope[varname]['y'] = tslope + lslope

        sloplot.plot(tslopex,tslope,'o',label='Train')
        sloplot.plot(lslopex,lslope,'o',label='Leading')
        if tslopex and tslope and len(tslope)!=0 and len(tslopex)!=0:
            print fill, varname, ' train', np.polyfit(tslopex,tslope,1)
        print fill, varname, ' lead', np.polyfit(lslopex,lslope,1)
        a,b = np.polyfit(tslopex + lslopex, tslope + lslope,1)

        sloplot.plot(tslopex+lslopex, [i*a + b for i in tslopex + lslopex], label = 'fit all ' + str(a) + 'x + ' + str(b))


        sloplot.legend()
        trainplot.set_xlabel('Nonlinearity correction [%]', fontsize=14, horizontalalignment='right')
        trainplot.set_ylabel('$\Delta$' + varname + ' [%]', fontsize=14)
        leadplot.set_xlabel('Nonlinearity correction [%]', fontsize=14, horizontalalignment='right')
        leadplot.set_ylabel('$\Delta$' + varname + ' [%]', fontsize=14)
        sloplot.set_xlabel('SBIL', fontsize=14, horizontalalignment='right')
        sloplot.set_ylabel('Slope', fontsize=14)
        fig.add_subplot(leadplot)
        fig.add_subplot(trainplot)
        fig.add_subplot(sloplot)
    
    plotVar(xsecplot,df,'xsec',range(-5,6))  
    plotVar(capxplot,dfx,'$\Sigma_X$',range(-5,6))  
    plotVar(capyplot,dfy,'$\Sigma_Y$',range(-5,6))    
    
    # yl.set_xlabel('Nonlinearity correction [%]',fontsize=18,horizontalalignment='center')
    # yt.set_xlabel('Nonlinearity correction [%]',fontsize=18,horizontalalignment='center')
    # xsecl.set_ylabel('$\Delta \sigma_{vis}$ [%]',fontsize=18)
    # xl.set_ylabel("$\Delta \Sigma_X$ [%]",fontsize=18)
    # yl.set_ylabel("$\Delta \Sigma_Y$ [%]",fontsize=18)
    plot.savefig(detector + '/' + fill + '.png')
    # plot.show()
plot.close()
for k in globalSlope.keys():
    a,b = np.polyfit(globalSlope[k]['x'], globalSlope[k]['y'], 1)
    plot.plot(globalSlope[k]['x'], globalSlope[k]['y'], 'o', label=k + 'datapoints 6016 + 6194 + 6362')
    plot.plot(globalSlope[k]['x'], [a*i + b for i in globalSlope[k]['x']], label = str(a) + 'x + ' + str(b))
    plot.xlabel('SBIL', fontsize=14, horizontalalignment='right')
    plot.ylabel('Slope', fontsize=14)
    plot.legend()
    plot.savefig(detector + '/' + k + '_slope.png')
    plot.show()