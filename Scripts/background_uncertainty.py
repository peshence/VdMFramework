import tables
import pandas as pd
import numpy as np
import csv
from scipy import stats

removestrays = lambda a: np.array([False if i < 6e9 else True for i in a])
with tables.open_file('/brildata/vdmdata17/6016_1707280758_1707280928.hd5') as hd5:
    for r in hd5.root.beam:
        bunchlist1 = removestrays(r['bxintensity1'])
        bunchlist2 = removestrays(r['bxintensity2'])

        fillednoncolliding = (bunchlist1 | bunchlist2) & ~(bunchlist1 & bunchlist2)
        break

    b1 = bunchlist1 & ~bunchlist2
    b2 = bunchlist2 & ~bunchlist1

    bim1df = []
    bim2df = []
    for row in hd5.root.bcm1fpcvdlumi:
        bim1 = {}
        bim2 = {}
        for i, bx in enumerate(b1):
            if not bx: continue
            bim1[i]=row['bxraw'][i]
        for i, bx in enumerate(b2):
            if not bx: continue
            bim2[i]=row['bxraw'][i]
        bim1df.append(bim1)
        bim2df.append(bim2)
    #     bim.append(row['bxraw'][fillednoncolliding])
    
    # for r in bim:
    #     for i, bx in enumerate(b1):
    #         if not bx: continue
    #         bim1[i]=r[i]
    #     for i, bx in enumerate(b2):
    #         if not bx: continue
    #         bim2[i]=r[i]

bim1df = pd.DataFrame(bim1df)
bim2df = pd.DataFrame(bim2df)
bim1df.to_csv('bcm1fmib1.csv')
bim2df.to_csv('bcm1fmib2.csv')


av = {}
with open('mibBcmAv.csv','w') as f:
    wr =  csv.writer(f)
    wr.writerow(['bx1','bim1', 'bim1Std', 'bim1Sem', 'bx2', 'bim2', 'bim2Std', 'bim2Sem'])
    for bx1,bx2 in zip(bim1df,bim2df):
        wr.writerow([bx1, np.mean(bim1df[bx1]), np.std(bim1df[bx1]), stats.sem(bim1df[bx1]),
                     bx2, np.mean(bim2df[bx2]), np.std(bim2df[bx2]), stats.sem(bim2df[bx2])])
# for bx in bim1df:
#     print bx
#     av[bx] = {}
#     av[bx]['bim1'] = np.mean(bim1df[bx])
#     av[bx]['bim1Std'] = np.std(bim1df[bx])
#     av[bx]['bim2'] = np.mean(bim2df[bx])
#     av[bx]['bim2Std'] = np.std(bim2df[bx])

# pd.DataFrame.from_dict(av).to_csv('bimbav.csv')
        
    
