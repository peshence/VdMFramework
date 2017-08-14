
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
for hit in [i for i in j['hits']['hits'] if 'data' not in i ['_source'] or 'PLTSLINK' in i['_source']['data']['detector']]:
        requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])