import pandas as pd
import os
import re

dirs = os.listdir('Analysed_Data/')
pattern = re.compile('(.*)_[.^_]*')
scans = list(set([re.match(pattern,i).group(1) for i in dirs]))
for scan in scans:
    xsecs = {}
    capsigmasx = {}
    capsigmasy = {}
    for d in dirs:
        if scan not in d: continue
        f1 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/LumiCalibration_PLT_SG_' + d[:4] +'.csv'
        f2 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/LumiCalibration_PLT_DG_' + d[:4] +'.csv'
        f = f1 if os.path.exists(f1) else f2
        curxs = pd.DataFrame.from_csv(f)
        f1 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/SG_FitResults.csv'
        f2 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/DG_FitResults.csv'
        f = f1 if os.path.exists(f1) else f2
        cur = pd.DataFrame.from_csv(f)
        i = int(str(d[-1]))
        i = -1 * i if d[-2] == '-' else i
        capsigmasx.update({str(i):cur.CapSigma[:len(cur.CapSigma)/2]})
        capsigmasy.update({str(i):cur.CapSigma[len(cur.CapSigma)/2:]})
        xsecs.update({str(i):curxs.xsec})
    for k in capsigmasx.keys():
        capsigmasx.update({k+'_diff':[(i-j)*100/j for i,j in zip(capsigmasx[k],capsigmasx['0'])]})
        capsigmasy.update({k+'_diff':[(i-j)*100/j for i,j in zip(capsigmasy[k],capsigmasy['0'])]})
        xsecs.update({k+'_diff':[(i-j)*100/j for i,j in zip(xsecs[k],xsecs['0'])]})
    dfx = pd.DataFrame.from_dict(capsigmasx)
    dfx = dfx.loc[:,['-5','-4','-3','-2','-1','0','1','2','3','4','5','-5_diff','-4_diff','-3_diff','-2_diff','-1_diff','0_diff','1_diff','2_diff','3_diff','4_diff','5_diff']]
    dfx.index = cur.BCID[:len(cur.CapSigma)/2]
    dfx.to_csv(scan + 'x.csv')
    dfy = pd.DataFrame.from_dict(capsigmasy)
    dfy = dfy.loc[:,['-5','-4','-3','-2','-1','0','1','2','3','4','5','-5_diff','-4_diff','-3_diff','-2_diff','-1_diff','0_diff','1_diff','2_diff','3_diff','4_diff','5_diff']]
    dfy.index = cur.BCID[:len(cur.CapSigma)/2]
    dfy.to_csv(scan + 'y.csv')
    df = pd.DataFrame.from_dict(xsecs)
    df = df.loc[:,['-5','-4','-3','-2','-1','0','1','2','3','4','5','-5_diff','-4_diff','-3_diff','-2_diff','-1_diff','0_diff','1_diff','2_diff','3_diff','4_diff','5_diff']]
    df.index = curxs.BCID
    df.to_csv(scan + '.csv')
