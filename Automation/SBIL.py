import json
import pandas as pd
import os
import requests
import pickle
import numpy as np
import re
import datetime as dt

lumis = ['PLT', 'HFLumi', 'BCM1F', 'HFLumiET']
def repost(folder,fill):
    """"
    Fills in missing SBIL data, probably unneeded at this point
    """
    beamdata = pickle.load(open(folder+'cond/BeamCurrents_'+fill+'.pkl'))

    s1 = beamdata['Scan_1']
    b1 = [0 for i in range(3654)]
    b2 = [0 for i in range(3654)]
    bc1 = {i[0]:i[1] for i in s1[len(s1)/2][-2].items() if i[0]!='sum'}
    bc2 = {i[0]:i[1] for i in s1[len(s1)/2][-1].items() if i[0]!='sum'}

    for i in bc1:
        b1[int(i)]=bc1[i]
    for i in bc2:
        b2[int(i)]=bc2[i]
    bcp1 = [i*j/1e22 for i,j in zip(b1,b2)]


    s2 = beamdata['Scan_2']
    b1 = [0 for i in range(3654)]
    b2 = [0 for i in range(3654)]
    bc1 = {i[0]:i[1] for i in s2[len(s2)/2][-2].items() if i[0]!='sum'}
    bc2 = {i[0]:i[1] for i in s2[len(s2)/2][-1].items() if i[0]!='sum'}
    
    for i in bc1:
        b1[int(i)]=bc1[i]
    for i in bc2:
        b2[int(i)]=bc2[i]    
    bcp2 = [i*j/1e22 for i,j in zip(b1,b2)]

    if s1[0][1][0]=='X':
        bcx = bcp1
        bcy = bcp2
    else:
        bcx = bcp2
        bcy = bcp1
    t1 = dt.datetime.strptime(folder[-30:-16],'%d%b%y_%H%M%S')
    t2 = dt.datetime.strptime(folder[-15:-1],'%d%b%y_%H%M%S')
    td = t2-t1
    fit = 'SG' if td.total_seconds() <= 600 else 'DG'
    jsons = [i for i in os.listdir(folder) if fit in i]
    for lumi in lumis:
        # if lumi != 'HFLumiET':
        #     continue
        fitr = 'output\d+' + lumi + '(.*).json'
        for js in jsons:
            if 'v2' in js:
                continue
            try:
                if lumi in js and not (lumi == 'HFLumi' and 'HFLumiET' in js):
                    print folder,js
                    jd = json.load(open(folder + js))
                    sbil = []
                    sbil_err = []
                    for i,j,k,l,m in zip(jd['peak_x_bx'],bcx,jd['peak_y_bx'],bcy,jd['sigmavis_bx']):
                        try:
                            sbil.append(0 if m == 0 else (i*j + k*l)*11245/(2*m))
                            sbil_err.append(0)
                        except:
                            print type(i),type(j),type(k),type(l),type(m)
                            print i,j,k,l,m
                            input()
                    # for i,j,k,l,m in zip(jd['peak_x_bx_err'],bcx,jd['peak_y_bx_err'],bcy,jd['sigmavis_bx_err']):
                    #     sbil_err.append((i*j + k*j)/m)
                    sbil_av = np.mean([i for i in sbil if i !=0])
                    sbil_av_err = np.mean(sbil_err)
                    jd.update({'sbil_bx': sbil,'sbil_bx_err':sbil_err, 'sbil_avg':sbil_av, 'sbil_avg_err':0})
                    json.dump(jd,open(folder+js,'w'))
                    # input()
                    # jd.update({'fit': re.match(fitr, js).group(1)})
                    requests.post(
                        'http://srv-s2d16-22-01.cms:11001/vdm', json.dumps(jd))
            except:
                pass
repost('Analysed_Data/5878_27Jun17_172027_27Jun17_172420/', '5878')
    
# for f in os.listdir('Analysed_Data/'):
#     if f[0] != 'F':
#         repost('Analysed_Data/' + f + '/',f[:4])