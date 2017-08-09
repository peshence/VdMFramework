import requests
import argparse
import os
import json
import re
import datetime as dt


#lumis = ['HFLumi', 'HFLumiET']
#lumis = ['PLT', 'HFLumi', 'BCM1F', 'HFLumiET']
# lumis = ['PLT', 'HFOC', 'BCM1F', 'HFET']
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()


def repost(folder):
    t1 = dt.datetime.strptime(folder[-30:-16],'%d%b%y_%H%M%S')
    t2 = dt.datetime.strptime(folder[-15:-1],'%d%b%y_%H%M%S')
    td = t2-t1
    fit = 'SG' if td.total_seconds() <= 600 else 'DG'
    jsons = [i for i in os.listdir(folder) if fit in i]
    # for lumi in lumis:
        # if lumi != 'HFLumiET':
        #     continue
        #fitr = 'output\d+' + lumi + '(.*).json'
    for j in jsons:
        #if lumi in j and not (lumi == 'HFLumi' and 'HFLumiET' in j):
            jd = json.load(open(folder + j))
            print j
            if str.isdigit(str(jd['detector'][-1])) or jd['detector'] == 'PLTSLINK':
                continue
            jd['detector'] = 'HFOC' if jd['detector']=='HFLumi' else ('HFET' if jd['detector']=='HFLumiET' else jd['detector'])
            #jd.update({'fit': re.match(fitr, j).group(1)})
            print requests.post(
                'http://srv-s2d16-22-01.cms:11001/vdm', json.dumps(jd))


if args.file:
    repost(args.file)
else:
    for f in os.listdir('Analysed_Data/'):
        if f[0] != 'F' and int(f[:4])>6026:# and int(f[:4])<5980) : #f == '6016_28Jul17_100004_28Jul17_112346':
            print 'yes'
            repost('Analysed_Data/' + f + '/')# or int(f[:4])>=5980):
            #if f[0] != 'F': #and int(f[:4])>5750:
            #if f == '6016_28Jul17_055855_28Jul17_060431':

