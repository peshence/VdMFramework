import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from math import floor as floor, log10 as log10

fill = '6385'
folder = '/brildata/vdmoutput/Automation/Analysed_Data/'
scan=0

def ylim(axes,up=0.2,down=0.2):
    mx = 0
    mn=min(axes[0])
    for a in axes:
        mx = max(max(a),mx)
        mn = min(min(a),mn)
    plt.ylim(ymax=up*(mx-mn) + mx,ymin=mn-down*(mx-mn))

for f in os.listdir(folder):
    if fill not in f: continue

    df = pd.DataFrame.from_csv(folder+f +'/PLT/results/BeamBeam/LumiCalibration_PLT_SG_' + fill + '.csv')
    try:
        df = df[df.BCID!='sum']
    except:
        pass
    leadbool = [True if str(int(i)-1) not in list(df.BCID) else False for i in df.BCID]
    lead = df[leadbool]
    train = df[[not i for i in leadbool]]
    
    ylim([train.xsec,lead.xsec])

    plt.errorbar(train.BCID,train.xsec,yerr=train.xsecErr,fmt='o',label='Train')
    plt.errorbar(lead.BCID,lead.xsec,yerr=lead.xsecErr,fmt='o',label='Leading', color='red')
    plt.legend(loc=4)
    plt.ylabel('$\sigma_{vis} [\mu b]$', fontsize=20)
    plt.xlabel('BCID', fontsize=14)
    plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
    plt.figtext(0.29,0.8,'Preliminary',fontsize=18,style='italic',backgroundcolor='white')
    plt.savefig('sigvis_' + fill + '_' + str(scan) + '.png')
    # plt.close()
    plt.show()


    ylim([df.SBIL])
    plt.errorbar(df.BCID,df.SBIL,fmt='o',yerr=df.SBILErr)
    # plt.legend()
    plt.ylabel('$SBIL [Hz/{\mu b}]$', fontsize=16)
    plt.xlabel('BCID', fontsize=14)
    plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
    plt.figtext(0.29,0.8,'Preliminary',fontsize=18,style='italic',backgroundcolor='white')
    plt.savefig('sbil_' + fill + '_' + str(scan) + '.png')
    # plt.close()
    plt.show()

    ylim([train.xsec,lead.xsec])
    plt.errorbar(train.SBIL,train.xsec,yerr=train.xsecErr,xerr=train.SBILErr,fmt='o',label='Train')
    plt.errorbar(lead.SBIL,lead.xsec,yerr=lead.xsecErr,xerr=lead.SBILErr,fmt='o',label='Leading', color='red')
    plt.legend(loc=4)
    plt.ylabel('$\sigma_{vis} [\mu b]$', fontsize=20)
    plt.xlabel('$SBIL [Hz/{\mu b}]$', fontsize=14)
    plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
    plt.figtext(0.29,0.8,'Preliminary',fontsize=18,style='italic',backgroundcolor='white')
    plt.savefig('sigvis(SBIL)_' + fill + '_' + str(scan) + '.png')
    # plt.close()
    plt.show()
    if scan==0:
        earlylead = lead
        earlytrain = train
    else:
        latelead = lead
        latetrain = train
    scan = scan+1

ylim([pd.concat([earlytrain.xsec,latetrain.xsec]),pd.concat([earlylead.xsec,latelead.xsec])],down=0.25)
plt.errorbar(pd.concat([earlytrain.SBIL,latetrain.SBIL]),pd.concat([earlytrain.xsec,latetrain.xsec]),fmt='o',yerr=pd.concat([earlytrain.xsecErr,latetrain.xsecErr]),xerr=pd.concat([earlytrain.SBILErr,latetrain.SBILErr]), label='Train')
plt.errorbar(pd.concat([earlylead.SBIL,latelead.SBIL]),pd.concat([earlylead.xsec,latelead.xsec]),fmt='o',yerr=pd.concat([earlylead.xsecErr,latelead.xsecErr]),xerr=pd.concat([earlylead.SBILErr,latelead.SBILErr]), label='Lead',color='red')
# plt.errorbar(latetrain.SBIL,latetrain.xsec,fmt='o',yerr=latetrain.xsecErr,xerr=latetrain.SBILErr, label='Late Scan Train')
# plt.errorbar(earlylead.SBIL,earlylead.xsec,fmt='o',yerr=earlylead.xsecErr,xerr=earlylead.SBILErr, label='Early Scan Leading')
# plt.errorbar(latelead.SBIL,latelead.xsec,fmt='o',yerr=latelead.xsecErr,xerr=latelead.SBILErr, label='Late Scan Leading')

def plotfit(x,y,name,color=None):
        (la,lb), cov = np.polyfit(x, y, 1,cov=True)
        def round_to_sign(x):
            return round(x, -int(floor(log10(abs(x))))+1)
        # la = la/np.mean(y)
        # lb = lb/np.mean(y)
        # cov[0][0]  = cov[0][0]/np.mean(y)
        # cov[1][1] = cov[1][1]/np.mean(y)
        lae = round_to_sign(cov[0][0])
        lbe = round_to_sign(cov[1][1])
        la = round(la,len(str(lae)) - '{0:f}'.format(lae).index('.') - 1)
        lb = round(lb,len(str(lbe)) - '{0:f}'.format(lbe).index('.') - 1)
        if color:
            plt.plot(x, [la*i + lb for i in x], label = name + ' (' + str(la) + '$\pm$' + str(lae) + ')x + ' + str(lb) + '$\pm$' + str(lbe),color=color)
        else:
            plt.plot(x, [la*i + lb for i in x], label = name + ' (' + str(la) + '$\pm$' + str(lae) + ')x + ' + str(lb) + '$\pm$' + str(lbe))

plotfit(pd.concat([earlytrain.SBIL,latetrain.SBIL]),pd.concat([earlytrain.xsec,latetrain.xsec]),'Train')
plotfit(pd.concat([earlylead.SBIL,latelead.SBIL]),pd.concat([earlylead.xsec,latelead.xsec]),'Lead',color='cyan')

plt.legend(loc=4,fontsize=12)

plt.ylabel('$\sigma_{vis} [\mu b]$', fontsize=20)
plt.xlabel('$SBIL [Hz/{\mu b}]$', fontsize=14)
plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
plt.figtext(0.29,0.8,'Preliminary',fontsize=18,style='italic',backgroundcolor='white')
plt.savefig('sigvis(SBIL)_' + fill + '_bothscans.png')
# plt.close()
plt.show()

