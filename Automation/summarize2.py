import json
import matplotlib.pyplot as plt
import os

folder = '/cmsnfsbrildata/brildata/vdmoutput/Automation/Analysed_Data/'
#name = '5718_27May17_214831_27May17_221433'
#name = '5730_30May17_173019_30May17_175214'
name = '5746_05Jun17_031739_05Jun17_034851'
lumis = ['PLT']#,'HFLumi', 'BCM1F', 'HFLumiET']
cols = ['peak_x_bx', 'capsigma_x_bx', 'peak_y_bx', 'capsigma_y_bx']
sigma = 'sigmavis_bx'

for lumi in lumis:
    jsons = [i for i in os.listdir(folder+name) if i[-4:] == 'json' and lumi in i]

    jsd = folder + name + '/' + [i for i in jsons if 'DG' in i][0]
    jss = folder + name + '/' + [i for i in jsons if 'SG' in i][0]
    jd = json.load(open(jsd))
    js = json.load(open(jss))
    plt.subplot(2,1,1)
    key = sigma
    ddata = [i for i in jd[key]]# if i != 0]
    sdata = [i for i in js[key]]# if i != 0]
    data = [(k,j/i) for k,(i,j) in enumerate(zip(ddata,sdata)) if j!=0 ]
    plt.plot([i[0] for i in data], [i[1] for i in data],'ro')
    plt.title(key +' '+ name)
    for l,key in enumerate(cols):
            ddata = [i for i in jd[key]]# if i != 0]
            sdata = [i for i in js[key]]# if i != 0]
            data = [(k,j/i) for k,(i,j) in enumerate(zip(ddata,sdata)) if j!=0 ]
            
            plt.subplot(2,4,l+5)
            plt.plot([i[0] for i in data], [i[1] for i in data],'ro')
            plt.title(key)
            
    #plt.savefig(folder + name + '/' + name+'.png', dpi = 500)
    plt.show()