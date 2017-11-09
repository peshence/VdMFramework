## ratios with train distinction commented and scan distinction
import json
import matplotlib.pyplot as plot
import csv
import os
import argparse
freq = 11265
sigvis = {
    'PLT':lambda a: 297,
    'HFET':lambda a: 2565,
    'BCM1FPCVD':lambda a: 203.8 if a in ['6336', '6348'] else 211.359
}
eta = 0.00867


curfol = os.path.abspath('../Analysed_Data/') + '/'

parser = argparse.ArgumentParser()
parser.add_argument('-l1','--lumi1')
parser.add_argument('-l2','--lumi2')
parser.add_argument('-i','--iterations')
args = parser.parse_args()
lead = args.iterations if args.iterations else 1
lumi1 = args.lumi1 if args.lumi1 else 'PLT'
lumi2 = args.lumi2 if args.lumi2 else 'HFET'

for folder in os.listdir(curfol):
    sbil = 2.9 if folder[:4] in ['6336', '6348'] else 3
    xsingle = []
    ysingle = []
    xlead = []
    ylead = []
    xtrain = []
    ytrain = []
    xlead2 = []
    ylead2 = []
    xlead3 = []
    ylead3 = []
    xlead4 = []
    ylead4 = []
    xlead5 = []
    ylead5 = []
    xlast = []
    ylast = []
    if folder[:4] == '6016' or folder == '6016_28Jul17_152753_28Jul17_155019': continue

    data = {}
    data1 = json.load(open(curfol + folder + '/LuminometerData/Rates_'
                           + lumi1 + '_' + folder[:4] + '.json'))
    data2 = json.load(open(curfol + folder + '/LuminometerData/Rates_'
                           + lumi2 + '_' + folder[:4] + '.json'))
    plot.rcParams["figure.figsize"] = (13, 10)
    # keydict = {}
    # keys = data1[data1.keys()[0]][0]['Rates'].keys()
    # keydict['single'] = [k for k in keys if k != 'sum' and str(int(k)+1) not in keys
    #                                         and str(int(k)-1) not in keys]
    for scan in data1.keys():
        keys = data1[scan][0]['Rates'].keys()
        for bx in keys:
            if bx == 'sum':
                continue
            bxdata1 = [i['Rates'][bx]*freq/sigvis[lumi1](folder[:4]) for i in data1[scan]]
            bxdata2 = [i['Rates'][bx]*freq/sigvis[lumi2](folder[:4]) for i in data2[scan]]

            if lumi1 == 'BCM1FPCVD': bxdata1 = [i + pow(i,2)*eta*(1+eta*sbil) for i in bxdata1]
            if lumi2 == 'BCM1FPCVD': bxdata2 = [i + pow(i,2)*eta*(1+eta*sbil) for i in bxdata2]

            if str(int(bx)-1) not in keys:
                if str(int(bx)+1) not in keys:
                    xsingle = xsingle + ([i for i in bxdata2 if i != 0])
                    ysingle = ysingle + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
                    continue
                xlead = xlead + ([i for i in bxdata2 if i != 0])
                ylead = ylead + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
                continue
            ## to separate 8b4e
            # if(int(bx)>1000):
            #     xtrain8b4e = xtrain8b4e + ([i for i in bxdata2 if i!=0])
            #     ytrain8b4e = ytrain8b4e + ([i/j for i,j in zip(bxdata1,bxdata2) if j!=0])
            #     continue
            # if (str(int(bx)-2) not in keys):
            #     xlead2 = xlead2 + ([i for i in bxdata2 if i != 0])
            #     ylead2 = ylead2 + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
            #     continue
            # if (str(int(bx)-3) not in keys):
            #     xlead3 = xlead3 + ([i for i in bxdata2 if i != 0])
            #     ylead3 = ylead3 + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
            #     continue
            # if (str(int(bx)-4) not in keys):
            #     xlead4 = xlead4 + ([i for i in bxdata2 if i != 0])
            #     ylead4 = ylead4 + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
            #     continue
            # if (str(int(bx)-5) not in keys and str(int(bx)-4) in keys):
            #     xlead5 = xlead5 + ([i for i in bxdata2 if i != 0])
            #     ylead5 = ylead5 + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
            #     continue
            # if (str(int(bx)+1) not in keys):
            #     xlast = xlast + ([i for i in bxdata2 if i != 0])
            #     ylast = ylast + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
            #     continue
            xtrain = xtrain + ([i for i in bxdata2 if i != 0])
            ytrain = ytrain + ([i/j for i,j in zip(bxdata1,bxdata2) if j != 0])
        ##to separate per scan
        # with open(folder[:4] + scan + 'train.csv', 'wb') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(('HFSBIL','PLT/HF'))
        #     writer.writerows(zip(xtrain,ytrain))
        # plot.plot(xtrain,ytrain,'o',label=scan+'train')
        # xtrain=[]
        # ytrain=[]

    #folder = '6016'
    plot.plot(xtrain,ytrain,'o',label = 'Train')
    plot.plot(xsingle,ysingle,'o',label = 'Single')
    plot.plot(xlead,ylead,'o',label = 'Lead')
    # plot.plot(xlead2,ylead2,'o',label='2nd in train')
    # plot.plot(xlead3,ylead3,'o',label='3rd in train')
    # plot.plot(xlead4,ylead4,'o',label='4th in train')
    # plot.plot(xlead5,ylead5,'o',label='5th in train')
    # plot.plot(xlast,ylast,'o',label='last in train')
    # plot.plot(xtrain8b4e,ytrain8b4e,'o',label='Train8b4e')
    plot.legend()
    plot.title(folder[:4] + lumi1 + '/' + lumi2 + '(' + lumi2 + 'SBIL)bcmlin')
    # plot.show()
    plot.savefig(folder[:4] + lumi1 + lumi2 + 'Ratio(' + lumi2 + 'SBIL)bcmlin.png',dpi=150,format='png')
    plot.close()
    with open(folder[:4] + 'single.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow((lumi2 + 'SBIL',lumi1 + '/' + lumi2))
        writer.writerows(zip(xsingle,ysingle))

    with open(folder[:4] + 'lead.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow((lumi2 + 'SBIL',lumi1 + '/' + lumi2))
        writer.writerows(zip(xlead,ylead))

    with open(folder[:4] + 'lead2.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow((lumi2 + 'SBIL',lumi1 + '/' + lumi2))
        writer.writerows(zip(xlead2,ylead2))

    with open(folder[:4] + 'trainno2.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow((lumi2 + 'SBIL',lumi1 + '/' + lumi2))
        writer.writerows(zip(xtrain,ytrain))


# with open('train8b4e.csv', 'wb') as f:
#     writer = csv.writer(f)
#     writer.writerow(('HFSBIL','PLT/HF'))
#     writer.writerows(zip(xtrain8b4e,ytrain8b4e))