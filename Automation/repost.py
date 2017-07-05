import requests
import argparse
import os
import json
import re


lumis = ['PLT', 'HFLumi', 'BCM1F', 'HFLumiET']
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()


def repost(folder):
    jsons = [i for i in os.listdir(folder) if 'SG' in i or 'DG' in i]
    for lumi in lumis:
        # if lumi != 'HFLumiET':
        #     continue
        fitr = 'output\d+' + lumi + '(.*).json'
        for j in jsons:
            if lumi in j and not (lumi == 'HFLumi' and 'HFLumiET' in j):
                jd = json.load(open(folder + j))
                jd.update({'fit': re.match(fitr, j).group(1)})
                requests.post(
                    'http://srv-s2d16-22-01.cms:11001/vdmtest', json.dumps(jd))


if args.file:
    repost(args.file)
else:
    for f in os.listdir('Analysed_Data/'):
        if f[0] != 'F' and int(f[:4])>5750:
            repost('Analysed_Data/' + f + '/')
r = requests.get('http://srv-s2d16-22-01/es/data-vdm/_search?size=5000')
j = r.json()
for hit in [i for i in j['hits']['hits'] if i['_source']['data']['detector'] == 'HFLumiET' and i['_source']['data']['fill'] == 5839]:
        requests.delete('http://srv-s2d16-22-01/es/' + hit['_index'] + '/logs/' + hit['_id'])
