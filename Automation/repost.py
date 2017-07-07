import requests
import argparse
import os
import json
import re
import datetime as dt


#lumis = ['PLT', 'HFLumi', 'BCM1F', 'HFLumiET']
lumis = ['PLT', 'HFOC', 'BCM1F', 'HFET']
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()


def repost(folder):
    t1 = dt.datetime.strptime(folder[-30:-16],'%d%b%y_%H%M%S')
    t2 = dt.datetime.strptime(folder[-15:-1],'%d%b%y_%H%M%S')
    td = t2-t1
    fit = 'SG' if td.total_seconds() <= 600 else 'DG'
    jsons = [i for i in os.listdir(folder) if fit in i]
    for lumi in lumis:
        # if lumi != 'HFLumiET':
        #     continue
        fitr = 'output\d+' + lumi + '(.*).json'
        for j in jsons:
            if lumi in j and not (lumi == 'HFLumi' and 'HFLumiET' in j):
                jd = json.load(open(folder + j))                
                jd['detector'] = 'HFOC' if jd['detector']=='HFLumi' else ('HFET' if jd['detector']=='HFLumiET' else jd['detector'])
                #jd.update({'fit': re.match(fitr, j).group(1)})
                requests.post(
                    'http://srv-s2d16-22-01.cms:11001/vdm', json.dumps(jd))


if args.file:
    repost(args.file)
else:
    for f in os.listdir('Analysed_Data/'):
        if f[0] != 'F': #and int(f[:4])>5750:
            repost('Analysed_Data/' + f + '/')
# r = requests.get('http://srv-s2d16-22-01/es/data-vdm/_search?size=5000')
# j = r.json()
# for hit in [i for i in j['hits']['hits'] if i['_source']['data']['detector'] == 'HFLumiET' and i['_source']['data']['fill'] == 5839]:
#         requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])
