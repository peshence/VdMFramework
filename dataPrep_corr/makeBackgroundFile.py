import tables as t
import json

def removestrays:
    return np.array([0 if i < 6e9 else 1 for i in a])

def doMakeBackgroundFile(filename):
    with t.open_file(filename) as hd5:
        for row in hd5.root.beam:
            table = [(removestrays(r['bxintensity1']), removestrays(r['bxintensity2'])) for r in h5file.root.beam.where(tw)]
            bunchlist1 = [r[0] for r in table] 
            bunchlist2 = [r[1] for r in table] 

            if bunchlist1 and bunchlist2:
                collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
