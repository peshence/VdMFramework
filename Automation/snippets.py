
### READ DOWNLOADED JSON PLOTS
jsonFileName = r"C:\Users\ptsrunch\OneDrive\CERN\Technical\VdM offline automation\VdM\sigmavis.json"
jsonFile = open(jsonFileName, 'r')
jsonData = jsonFile.read()
sigmavis = json.loads(jsonData[3:])

df = pd.DataFrame(columns = ['Fill'] + lumis)
for i in sigmavis:
det = i['name'][22:]
for x,f,s in zip(i['x'], i['_other']['fill'],i['y']):
dfloc[x,det]=s
dfloc[x,'Fill']=f



### ratio between normalized detector peak rates
np.mean([rates['Scan_1'][3][3][0][i]*beams['Scan_2'][3][-1][i]*beams['Scan_2'][3][-2][i]/
        (rates['Scan_2'][3][3][0][i]*beams['Scan_1'][3][-1][i]*beams['Scan_1'][3][-2][i])
        for i in rates['Scan_1'][3][3][0].keys() if i!='sum'])
1.0020259308798483

### ratio between non normalized detector peak rates
np.mean([rates['Scan_1'][3][3][0][i]/rates['Scan_2'][3][3][0][i] for i in rates['Scan_1'][3][3][0].keys() if i!='sum'])
1.0043421343801477


fill = 6097
rateTable = 'pltlumizero'
scanpt = [1503006260.0,1503006220.0]
datapath = '/cmsnfsbrildata/brildata/vdmdata17/6097_1708172141_1708172152.hd5'

import dataPrepII.makeRateFile as mrf
import makeBeamCurrentFileII as mbcf

def UsingFrameWork(datapath, rateTable, scanpt, fill):
    r = mrf.getRates(datapath, rateTable, scanpt, fill)
    b = mbcf.getCurrents(datapath, scanpt, fill)
    avr = np.mean([r[0][k] for k in r[0].keys() if k !='sum'])
    avb1 = np.mean([b[2][k] for k in b[2].keys() if k !='sum'])
    avb2 = np.mean([b[3][k] for k in b[3].keys() if k !='sum'])
    print avr/avb1/avb2*1e22, avr

    





### get raw rates, beam currents and normalized rates for a scan into a csv 
### WRONG, includes unfilled bunches
# import tables
# h5 = tables.open_file('/cmsnfsbrildata/brildata/vdmdata17/6097_1708172141_1708172152.hd5')
# a = [(i['timestampsec'], i['bxraw']) for i in h5.root.pltlumizero]
# b = [(i['timestampsec'], i['bxintensity1'], i['bxintensity1']) for i in h5.root.beam]

# with open('6097_0.csv','w') as f:
#     out = csv.writer(f)
#     out.writerow(['timestamp', 'rate', 'beam1', 'beam2', 'normalized'])
#     for i,j in zip(a,b):
#         out.writerow((i[0], np.mean(i[1]), np.mean(j[1]), np.mean(j[2]), np.mean(i[1]) / (np.mean(j[1]) * np.mean(j[2]) / 1e22)))


filename = '/cmsnfsbrildata/brildata/vdmdata17/6097_1708172141_1708172152.hd5'

with tables.open_file(filename, 'r') as h5:
    removestrays = lambda a: np.array([0 if i < 6e9 else 1 for i in a])
    b = [(i['timestampsec'], removestrays(i['bxintensity1']), removestrays(i['bxintensity1'])) for i in h5.root.beam]
    bunchlist1 = [r[1] for r in b] 
    bunchlist2 = [r[2] for r in b] 
    if bunchlist1 and bunchlist2:
        collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
    a = [(i['timestampsec'], i['bxraw']) for i in h5.root.pltlumizero]
    b = [(i['timestampsec'], i['bxintensity1'], i['bxintensity1']) for i in h5.root.beam]
    bunchlist1 = [r[1] for r in b] 
    bunchlist2 = [r[2] for r in b] 
    if bunchlist1 and bunchlist2:
        collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
end = []
for i in a:
    data = {}
    j = [k for k in b if k[0] == i[0]]
    if j:
        j = j[0]
    else:
        continue
    data['timestamp'] = i[0]
    data['rates'] = {}
    data['beam1'] = {}
    data['beam2'] = {}
    for bcid in collBunches:
        data['normalized'] = {}
        data['rates'][bcid+1] = float(i[1][bcid])
        data['beam1'][bcid+1] = float(j[1][bcid])
        data['beam2'][bcid+1] = float(j[2][bcid])
        data['normalized'][bcid+1] = float(i[1][bcid] * 1e22 / (j[1][bcid] * j[2][bcid]))
    end.append(data)
    

json.dump(end,open('6097_0.json','w'))

import os
### use those jsons
names = [i for i in os.listdir('./') if i[-4:]=='json' and i[0] == '6']
for n in names:
    print n
    #n = '6016_0.json'
    with open(os.getcwd() +'/'+ n) as o:
        j = json.load(o)
        with open(os.getcwd() +'/'+n[:6] + '.csv','w') as f:
            out = csv.writer(f)
            out.writerow(['timestamp', 'rate', 'beam1', 'beam2', 'normalized'])
            for i in j:
                out.writerow((i['timestamp'], np.mean([i['rates'][k] for k in i['rates'].keys()]), np.mean([i['beam1'][k] for k in i['beam1'].keys()]), np.mean([i['beam2'][k] for k in i['beam2'].keys()]), np.mean([i['normalized'][k] for k in i['normalized'].keys()])))
                # out.writerow((i['timestamp'], i['rates'][u'343'], i['beam1'][u'343'], i['beam2'][u'343']))

# def notnull(arr):
#     return [i for i in arr if i != 0]

# ### use those jsons
# names = [i for i in os.listdir('./') if i[-4:]=='json' and i[0] == '6']
# for n in names:
#     with json.load(open(n)) as j:
#         for i in j:
#             with open(n[:6] + '.csv','w') as f:
#                 out = csv.writer(f)
#                 out.writerow(['timestamp', 'rate', 'beam1', 'beam2', 'normalized'])
#                 for i,j in zip(a,b):
#                     out.writerow((notnull(i['timestamp']), np.mean(notnull(i['rate'])), np.mean(notnull(i['beam1'])),
#                         np.mean(notnull(i['beam2'])), np.mean(notnull(i['rate'])) / (np.mean(notnull(i['beam1'])) * np.mean(notnull(i['beam1'])) / 1e22)))

early = json.load(open('/cmsnfsbrildata/brildata/vdmoutput/Automation/Analysed_Data/6140_27Aug17_202522_27Aug17_202854/output6140PLTSG1.json'))
late = json.load(open('/cmsnfsbrildata/brildata/vdmoutput/Automation/Analysed_Data/6140_28Aug17_094708_28Aug17_095059/output6140PLTSG1.json'))
x = []
y = []
xerr = []
yerr = []
for i,j,ie,je in zip(early['sigmavis_bx'],early['sbil_bx'],early['sigmavis_bx_err'],early['sbil_bx_err']):
    if i!=0:
            x.append(j)
            y.append(i)
            xerr.append(je)
            yerr.append(ie)

for i,j in zip(late['sigmavis_bx'],late['sbil_bx']):
    if i!=0:
            x.append(j)
            y.append(i)
            xerr.append(je)
            yerr.append(ie)


with open('6140xsec(sbil)_late' + '.csv','w') as f:
    out = csv.writer(f)
    out.writerow(['sbil','sbilerr','sigvis', 'sigviserr'])
    for i,j,k,l in zip(x,y,xerr,yerr):
        out.writerow((i,j,k,l))



### single bunch raw rates
import tables, pandas as pd, Configurator, numpy as np, matplotlib.pyplot as plt

h5 = tables.open_file('/cmsnfsbrildata/brildata/vdmdata17/6259_1709302212_1709302224.hd5')
rateTable='bcm1fpcvdlumi'
for table in h5.root:
    if table.name == rateTable:
        beamtable = table
        break

times = Configurator.GetTimestamps(Configurator.RemapVdMDIPData(pd.DataFrame.from_records(h5.root.vdmscan[:])), 6259, 'test')
times = [[i[0][0],i[1][0]] for i in times]

data = []
for tp in times:
    tw = '(timestampsec >' + str(tp[0]) + ') & (timestampsec <=' +  str(tp[1]) + ')'
    table = [r['bxraw'] for r in beamtable.where(tw)]
    data =  data + table


dft = pd.DataFrame(data)
df = dft.transpose()

removestrays = lambda a: np.array([0 if i < 6e9 else 1 for i in a])
table = [(removestrays(r['bxintensity1']), removestrays(r['bxintensity2'])) for r in h5.root.beam.where(tw)]
bunchlist1 = [r[0] for r in table] 
bunchlist2 = [r[1] for r in table]
collBunches  = np.nonzero(bunchlist1[0]*bunchlist2[0])[0].tolist()
print collBunches
dfcsv = pd.DataFrame()
dfcsv[9] = df.iloc[9]
dfcsv[90] = df.iloc[90]
plt.plot(df.iloc[9], 'ro', label='BCID 9')
plt.plot(df.iloc[90], 'bo', label='BCID 90')
plt.legend()
plt.show()

dfcsv = pd.DataFrame()
dfcsv[2825] = df.iloc[2825]
dfcsv[2809] = df.iloc[2809]
dfcsv[781] = df.iloc[781]
dfcsv[785] = df.iloc[785]
dfcsv[90] = df.iloc[90]
dfcsv.to_csv('hfetreducedmu6194rates.csv')
plt.plot(df.iloc[2809], 'mo')
plt.plot(df.iloc[2825], 'co')
plt.plot(df.iloc[785], 'bo')
plt.plot(df.iloc[781], 'ro')
plt.plot(df.iloc[90], 'go')
plt.show()


for i,j in enumerate(df.iterrows()):
    if i in collBunches:
        if i-1 in collBunches:
            plt.plot(j[1],'ro')
        elif i+1 in collBunches:
            plt.plot(j[1],'bo')
        else:
            plt.plot(j[1],'go')




plt.show()


### calculating sigmavis with adjusted peak (+const)
import numpy as np,pandas as pd,matplotlib.pyplot as plt
fr = pd.DataFrame.from_csv('/cmsnfsbrildata/brildata/vdmoutput/Automation/Analysed_Data/6259_01Oct17_001440_01Oct17_001718/BCM1FPCVD/results/BeamBeam/SGConst_FitResults.csv')
fr = fr.loc[fr.BCID!='sum']
fr1 = fr.iloc[:1909]
fr2 = fr.iloc[1909:]
old = []
for s1,s2,p1,p2 in zip(fr1.CapSigma,fr2.CapSigma, fr1.peak,fr2.peak):
    old.append(np.pi*s1*s2*(p1+p2))


new = []
for s1,s2,p1,p2,c1,c2 in zip(fr1.CapSigma,fr2.CapSigma, fr1.peak,fr2.peak,fr1.Const,fr2.Const):
    new.append(np.pi*s1*s2*(p1+p2+c1+c2))


wtf = []
for s1,s2,p1,p2,c1,c2 in zip(fr1.CapSigma,fr2.CapSigma, fr1.peak,fr2.peak,fr1.Const,fr2.Const):
    wtf.append((np.pi*s1*s2+0.043093*c1/2 + 0.030781*c2/2)*(p1+p2+c1+c2))



plt.plot(fr1.BCID,old,'ro',label='Gaussian Peak')
plt.plot(fr1.BCID,new,'bo',label='Peak+Const')
plt.plot(fr1.BCID,wtf,'go',label='wtf')
plt.legend()
plt.show()

0.043093 0.030781


import json
import pandas as pd
import os
fills = [6275,6283,6287,6288,6291]
lumi = 'BCM1FPCVD'
folder = '/brildata/vdmoutput/Automation/Analysed_Data/'
keys = ['timestamp', 'fill', 'fit', 'sigmavis_avg', 'sbil_avg']
df = pd.DataFrame()
allscans = os.listdir(folder)
for name in allscans:
    if (not str.isdigit(str(name[0]))) or (int(name[:4]) not in fills):
        continue
    jsons = [i for i in os.listdir(folder+name) if i[-4:] == 'json' and lumi in i]
    for jsonFile in jsons:
        with open(folder+name+'/'+jsonFile) as f:
            data = json.load(f)
        row = {}
        row.update({'scannum':})
        for key in keys:
            row.update({key:data[key]})
        if df.empty:
            df = pd.DataFrame(data=row,index=[0])
        else:
            df = df.append(row,ignore_index=True)
            
fits = list(set(df.fit))
for fit in fits:
    tempdf = df.loc[df.fit==fit]
    plt.plot(tempdf.timestamp,tempdf.sigmavis_avg,'o',label=fit)


plt.legend()
plt.show()

###ratios plots
import json
import matplotlib.pyplot as plot
import os
curfol = os.path.abspath('../Analysed_Data/') + '/'
for folder in os.listdir(curfol):
    hf = json.load(open(curfol + folder + '/LuminometerData/Rates_HFET_' + folder[:4] + '.json'))
    plt = json.load(open(curfol + folder + '/LuminometerData/Rates_PLT_' + folder[:4] + '.json'))
    freq = 11265
    pltsig = 297
    hfsig = 2565
    if not os.path.exists(folder): os.mkdir(folder)
    for scan in plt.keys():
        for bx in plt[scan][0]['Rates'].keys():
            plot.close()
            single = [i['Rates'][bx]*freq/pltsig for i in plt[scan]]
            singlehf = [i['Rates'][bx]*freq/hfsig for i in hf[scan]]
            plot.rcParams["figure.figsize"] = (13,10)
            plot.subplot(3,1,1)
            plot.plot(single, label='PLT')
            plot.plot(singlehf, label='HF')
            plot.title('SBIL(step)')
            plot.legend()
            plot.subplot(3,1,2)
            plot.plot([i/j for i,j in zip(single,singlehf) if j!=0])
            plot.title('PLT/HF(step)')
            plot.subplot(3,1,3)
            plot.plot([i for i in singlehf if i!=0],[i/j for i,j in zip(single,singlehf) if j!=0],'o')
            plot.title('PLT/HF(HFSBIL)')
            #plot.show()
            plot.savefig(folder + '/' + scan + 'bx' + bx + '.png',dpi=150,format='png')
        

###simple rateplots
def get(lumitable):
    raw = []
    bx = []
    for row in lumitable:
        bx.append(row['bx'])
        raw.append(row['bxraw'])
    return bx,raw 


def plot(m,n):
    res = []
    for i in m:
        res.append(i[n])
    plt.plot(res)


def pl(m,n):
    plot(m,n)
    plt.show()


