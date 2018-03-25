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
parser.add_argument('-pc', '--perchannel', action='store_true')
args = parser.parse_args()


def repost(folder, perchannel):
    if perchannel:
        repostperchannel(folder)
    else:
        repostnormal(folder)

def repostperchannel(folder):
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
            if not str.isdigit(str(jd['detector'][-1])):
                continue
            
            print j
            if not os.path.exists(folder + 'PerChannelJSONS/'):
                os.mkdir(folder + 'PerChannelJSONS/')
            if str.isdigit(str(jd['detector'][-2])):
                channel = int(str(jd['detector'][-2:]))
            else:
                channel = int(str(jd['detector'][-1]))
            detector = jd['detector']
            detector = re.match('([A-Z1]*[A-Z])_?[0-9]*', detector).group(1)
            jd['detector'] = detector
            jd.update({'channel':channel})
            #jd.update({'fit': re.match(fitr, j).group(1)})
            json.dump(jd,open(folder + 'PerChannelJSONS/' + j, 'w'))
            print requests.post(
                'http://srv-s2d16-22-01.cms:11001/vdmch', json.dumps(jd))
            




def repostnormal(folder):
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
                'http://srv-s2d16-22-01.cms:11001/vdmtest', json.dumps(jd))



if args.file:
    repost(args.file, args.perchannel)
else:
    for f in os.listdir('/brildata/vdmoutput/Automation/Analysed_Data/'):
        if f[0] != 'F' and int(f[:4])<6052 and int(f[:4])<5980 : #f == '6016_28Jul17_100004_28Jul17_112346':
            print 'yes'
            repost('/brildata/vdmoutput/Automation/Analysed_Data/' + f + '/', args.perchannel)# or int(f[:4])>=5980):
            #if f[0] != 'F': #and int(f[:4])>5750:
            #if f == '6016_28Jul17_055855_28Jul17_060431':

