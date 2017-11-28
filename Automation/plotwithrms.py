import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.DataFrame.from_csv('/cmsnfsbrildata/brildata/vdmoutput/AutomationSingelEff0/Analysed_Data/6362_05Nov17_182035_05Nov17_182308/PLT/results/BeamBeam/LumiCalibration_PLT_SG_6362.csv')
df.index = df.BCID
lead = df.loc[[i for i in df.index if int(i)-1 not in df.index],:]
train = df.loc[[i for i in df.index if int(i)-1 in df.index],:]
def plot(df,name):
    plt.errorbar(df.BCID,df.xsec,yerr=df.xsecErr,fmt='o', label=name)

plot(lead, 'Leading bunches')
plot(train, 'Train bunches')
plt.legend()
plt.title('Fill 6362 $\sigma_{vis}$')
plt.ylabel('$\sigma_{vis}$ $\mu b$')
plt.xlabel('BCID')

mean = np.mean(df.xsec)
plt.plot(df.BCID,[mean for i in df.BCID])
rms = np.sqrt(np.mean(np.square([mean - i for i in df.xsec])))

plt.plot(df.BCID,[mean+rms for i in df.BCID])
plt.plot(df.BCID,[mean-rms for i in df.BCID])
plt.show()