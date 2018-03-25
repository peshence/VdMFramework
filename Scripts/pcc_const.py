import pickle as pkl

old = '/afs/cern.ch/user/p/ptsrunch/LiteVdM/Fill6016_Jul282017/LuminometerData/Rates_PCC_6016_old.pkl'
new = '/afs/cern.ch/user/p/ptsrunch/LiteVdM/Fill6016_Jul282017/LuminometerData/Rates_PCC_6016.pkl'
const = 0.8

with open(old,'r') as f:
    data = pkl.load(f)

for scannum in data:
    for row in data[scannum]:
        for bcid in row[3][0] :
            row[3][0][bcid] = row[3][0] [bcid] - const

with open(new,'w') as f:
    pkl.dump(data,f)


