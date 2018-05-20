### THIS CODE SHOULD ONLY BE USED IF YOU COMPLETELY UNDERSTAND IT AND AFTER EDITING TO SUIT YOUR NEEDS
### Delete records in batches
import requests
# from multiprocessing import Process

# threads = []
url = 'http://srv-s2d16-22-01/es'
scroll_params = {
    'size':300,
    'scroll': '1m'
}
r = requests.get(url + '/data-vdm/_search', params=scroll_params)
j = r.json()
scroll_id = j['_scroll_id']

while True:
    scroll_params = {
        'scroll': '1m',
        'scroll_id': scroll_id
    }
    r = requests.get(url + '/_search/scroll', params=scroll_params)
    if r.status_code != 200:
        print r.text
        break
        # here handle failure
    j = r.json()
    print len(j['hits']['hits'])
    if len(j['hits']['hits']) == 0:
        break
    scroll_id = j['_scroll_id']
    for hit in [i for i in j['hits']['hits'] if 'data' not in i['_source'] or (i['_source']['data']['fill'] == 6592 and (i['_source']['data']['detector']=='HFOC' or i['_source']['data']['detector']=='HFET'))]:
        requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])
    
## this part doesn't work as intended
#     p = Process(target=deletescans,args=(j,))
#     threads.append(p)
#     p.start()
# for th in threads:
#     th.join()


# Simpler version without scroll, works with smaller dbs
# ### DELETE RECORDS
# import requests
# import json
# r = requests.get('http://srv-s2d16-22-01/es/data-vdm-2018/_search?size=1000')
# j = r.json()
# for hit in [i for i in j['hits']['hits'] if 'data' not in i['_source'] or ((i['_source']['data']['fill'] == 6545 or i['_source']['data']['fill'] == 6553) and i['_source']['data']['detector']=='plt')]:
#         requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])
# for hit in [i for i in j['hits']['hits'] if 'data' not in i['_source'] or i['_source']['data']['timestamp'] == 1501231474 or i['_source']['data']['timestamp'] == 1501228894]:
#         requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])