
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
r = requests.get('http://srv-s2d16-22-01/es/data-vdmtest/_search?size=5000')
j = r.json()
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



with open('6097_0.csv','w') as f:
    out = csv.writer(f)
    out.writerow(['timestamp', 'rate', 'beam1', 'beam2'])
    for i,j in zip(a,b):
        out.writerow((i[0], np.mean(i[1]), np.mean(j[1]), np.mean(j[2])))

