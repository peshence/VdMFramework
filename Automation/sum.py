import pandas as pd
import os
import re

dirs = os.listdir('Analysed_Data/')
pattern = re.compile('(.*)_[.^_]*')
scans = list(set([re.match(pattern,i).group(1) for i in dirs]))
for scan in scans:
    xsecs = {}
    for d in dirs:
        if scan not in d: continue
        f1 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/LumiCalibration_PLT_SG_' + d[:4] +'.csv'
        f2 = 'Analysed_Data/' + d + '/PLT/results/BeamBeam/LumiCalibration_PLT_DG_' + d[:4] +'.csv'
        f = f1 if os.path.exists(f1) else f2
        cur = pd.DataFrame.from_csv(f)
        i = int(str(d[-1]))
        i = -1 * i if d[-2] == '-' else i
        xsecs.update({str(i):cur.xsec})
    df = pd.DataFrame.from_dict(xsecs)
    df.index = cur.BCID
    df.to_csv(scan + '.csv')

