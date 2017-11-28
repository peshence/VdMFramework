import VdManalyze as v
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# df = v.load_all(['PLT'],6300,6372)
ldf = v.load_all(['PLT','HFET'], 6300, 6372, leading=True)
tdf = v.load_all(['PLT','HFET'], 6300, 6372, train=True)

plt.errorbar(tdf.PLT_SBIL,tdf.PLT_sigmavis,yerr=tdf.PLT_sigmavis_err,fmt='o',label='Train')
plt.errorbar(ldf.PLT_SBIL,ldf.PLT_sigmavis,yerr=ldf.PLT_sigmavis_err,fmt='o',label='Leading')

def round_to_sign(x):
    return round(x, -int(np.floor(np.log10(abs(x))))+1)

def plotfit(x,y,sigma):
    (a,b), cov = np.polyfit(x, y, 1, w=[1/i for i in sigma], cov=True)
    mean = np.mean(y)
    la,lb = a,b
    la = la/mean*100
    cov[0][0] = cov[0][0]/mean*100
    lae = round_to_sign(cov[0][0])
    lbe = round_to_sign(cov[1][1])
    la = round(la,len(str(lae)) - '{0:f}'.format(lae).index('.') - 1)
    lb = round(lb,len(str(lbe)) - '{0:f}'.format(lbe).index('.') - 1)
    plt.plot(x, [a*i + b for i in x], label = '(' + str(la) + '$\pm$' + str(lae) + ')%x + ' + str(lb) + '$\pm$' + str(lbe))
print(type(tdf.PLT_SBIL[0]), type(tdf.PLT_sigmavis[0]), type(tdf.PLT_sigmavis_err[0]))
plotfit([float(i) for i in tdf.PLT_SBIL],tdf.PLT_sigmavis,tdf.PLT_sigmavis_err)
plotfit([float(i) for i in ldf.PLT_SBIL],ldf.PLT_sigmavis,ldf.PLT_sigmavis_err)
plt.legend()
plt.title('PLT $\sigma_{vis}$ average per fill for fills 6300-6371')
plt.ylabel('$\sigma_{vis}$ $\mu b$')
plt.xlabel('BCID')
plt.show()

plt.errorbar(tdf.HFET_SBIL,tdf.HFET_sigmavis,yerr=tdf.HFET_sigmavis_err,fmt='o',label='Train')
plt.errorbar(ldf.HFET_SBIL,ldf.HFET_sigmavis,yerr=ldf.HFET_sigmavis_err,fmt='o',label='Leading')

def round_to_sign(x):
    return round(x, -int(np.floor(np.log10(abs(x))))+1)

def plotfit(x,y,sigma):
    (a,b), cov = np.polyfit(x, y, 1, w=[1/i for i in sigma], cov=True)
    mean = np.mean(y)
    la,lb = a,b
    la = la/mean*100
    cov[0][0] = cov[0][0]/mean*100
    lae = round_to_sign(cov[0][0])
    lbe = round_to_sign(cov[1][1])
    la = round(la,len(str(lae)) - '{0:f}'.format(lae).index('.') - 1)
    lb = round(lb,len(str(lbe)) - '{0:f}'.format(lbe).index('.') - 1)
    plt.plot(x, [a*i + b for i in x], label = '(' + str(la) + '$\pm$' + str(lae) + ')%x + ' + str(lb) + '$\pm$' + str(lbe))
print(type(tdf.HFET_SBIL[0]), type(tdf.HFET_sigmavis[0]), type(tdf.HFET_sigmavis_err[0]))
plotfit([float(i) for i in tdf.HFET_SBIL],tdf.HFET_sigmavis,tdf.HFET_sigmavis_err)
plotfit([float(i) for i in ldf.HFET_SBIL],ldf.HFET_sigmavis,ldf.HFET_sigmavis_err)
plt.legend()
plt.title('HFET $\sigma_{vis}$ average per fill for fills 6300-6371')
plt.ylabel('$\sigma_{vis}$ $\mu b$')
plt.xlabel('BCID')
plt.show()