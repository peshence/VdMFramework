import requests
import json
import numpy as np
import os
import re

threads = []
# url = 'http://srv-s2d16-22-01/es/'
url = 'http://srv-s2d16-22-01'
post = ':11001/'
get = '/es/'
dataindex = 'vdm'
# scroll_params = {
#     'size':100,
#     'scroll': '1m'
# }
# r = requests.get(url + get + 'data-' + dataindex + '/_search', params=scroll_params)
# j = r.json()
# scroll_id = j['_scroll_id']

# hits = j['hits']['hits']
# print len(hits)
# while True:
#     scroll_params = {
#         'scroll': '1m', 
#         'scroll_id': scroll_id,
#         'size':100
#     }
#     print scroll_params['scroll_id']
#     r = requests.get(url + get + '_search/scroll', params=scroll_params)
#     if r.status_code != 200:
#         print r.text
#         print 'statuscode 200'
#         break
#         # here handle failure
#     j = r.json()
#     print len(j['hits']['hits'])
#     for hit in j['hits']['hits']:
#         try:
#             print hit['_source']['data']['timestamp']
#             break
#         except:
#             continue
#     if len(j['hits']['hits']) == 0:
#         break
#     hits = hits + j['hits']['hits']
#     scroll_id = j['_scroll_id']
#     print scroll_id


vdmemit = {}
# with open('web.json','w') as f:
#     json.dump(hits,f)

# requests.delete(url + get + 'data-' + dataindex + '-*')
# with open('/brildata/vdmoutput/Automation/web.json','r') as f:
#     hits = json.load(f)
# for hit in hits:
#     if 'data' in hit['_source']:
#         data = hit['_source']['data']
#         if data['timestamp'] == 1501214335:
#             vdmemit[data['detector']] = data['sigmavis_avg']
# for hit in hits:
#     if 'data' in hit['_source']:
#         data = hit['_source']['data']
automation = '/brildata/vdmoutput/Automation/Analysed_Data/'
ratiofolder = '6016_28Jul17_055855_28Jul17_060210'
for j in os.listdir(automation+ratiofolder):
    if j[-4:]!='json': continue
    with open(automation+ratiofolder+'/' +j) as f:
        data = json.load(f)
    vdmemit[data['detector']] = data['sigmavis_avg']
for folder in os.listdir(automation):
    for js in os.listdir(automation+folder):
        if js[-4:]!='json' or 'UTCA' in js or re.match('output\d{4}[A-Z1]*([_0-9]*)[A-Za-z]*\d?\.json',js).groups()[0]!='': continue
        print js
        with open(automation+folder+'/' +js) as f:
            data = json.load(f)
        if data['fill']==6399 and data['detector']=='PLT':break
        if data['detector'] == 'BCM1F':
            data['detector'] = 'BCM1FPCVD'
        if data['sigmavis_avg'] < 0 or data['sigmavis_avg'] > 5000 or data['detector'] not in vdmemit.keys():
            continue
        sig = data['sigmavis_bx']
        sbil = data['sbil_bx']
        lsig,lsbil,tsig,tsbil = [],[],[],[]
        for i,j in enumerate(sig):
            if j!=0:
                if i==0 or sig[i-1]==0:
                    lsig.append(j)
                    lsbil.append(sbil[i])
                else:
                    tsig.append(j)
                    tsbil.append(sbil[i])

        lm = np.mean(lsig)        
        lsbil = [i/j*lm for i,j in zip(lsbil,lsig)]
        try:
            (la,lb),lcov = np.polyfit(lsbil,lsig, 1, cov=True)

            data['linearity_lead'] = la*100/lm
            data['linearity_lead_err'] = lcov[0,0]*100/lm
        except:
            print 'leading', data['detector'], data['fill'], data['timestamp'], lsbil,lsig
    
        data['efficiency_lead'] = lm/vdmemit[data['detector']]
        data['efficiency_lead_err'] = np.std(lsig)/vdmemit[data['detector']]

        if tsig and len(tsig)>0:
            tm = np.mean(tsig)
            tsbil = [i/j*tm for i,j in zip(tsbil,tsig)]
            try:
                (ta,tb),tcov = np.polyfit(tsbil,tsig, 1, cov=True)

                data['linearity_train'] = ta*100/tm
                data['linearity_train_err'] = tcov[0,0]*100/tm
            except:
                'train', data['detector'], data['fill'], data['timestamp'], tsbil,tsig

            data['efficiency_train'] = lm/vdmemit[data['detector']]
            data['efficiency_train_err'] = np.std(tsig)/vdmemit[data['detector']]

        with open(automation+folder+'/'+js,'w') as f:
            json.dump(data,f)

        requests.post(url + post + dataindex, json.dumps(data))

# t = threading.Thread(target=deletescans,args=(j,))
# t.start()
# threads.append(t)
# for th in threads:
#     th.join()