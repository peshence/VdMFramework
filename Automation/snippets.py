
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


### DELETE RECORDS
r = requests.get('http://srv-s2d16-22-01/es/data-vdmch/_search?size=1000')
j = r.json()
for hit in [i for i in j['hits']['hits'] if 'data' not in i['_source'] or i['_source']['data']['fill'] == 6152 and 'DG' in i['_source']['data']['fit']]:
        requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])
for hit in [i for i in j['hits']['hits'] if 'data' not in i['_source'] or i['_source']['data']['timestamp'] == 1501231474 or i['_source']['data']['timestamp'] == 1501228894]:
        requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])

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


