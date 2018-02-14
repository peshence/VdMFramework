import matplotlib.pyplot as plt
import pandas as pd


l = pd.DataFrame.from_csv('PLT_const_leading_2017.csv')
t = pd.DataFrame.from_csv('PLT_const_train_2017.csv')

l = l[[False if not i or abs(j)>abs(i)/2 or k<1 else True for i,j,k in zip(l['PLT_Slope[%]'],l['PLT_SlopeAbsErr[%]'],l['PLT_SBIL'])]]
t = t[[False if not i or abs(j)>abs(i)/2 or k<1 else True for i,j,k in zip(t['PLT_Slope[%]'],t['PLT_SlopeAbsErr[%]'],t['PLT_SBIL'])]]

plt.ylim(ymin=-1,ymax=2.7)
plt.errorbar(t.PLT_SBIL,t['PLT_Slope[%]'],yerr=t['PLT_SlopeAbsErr[%]'],fmt='o',label = 'train')
plt.errorbar(l.PLT_SBIL,l['PLT_Slope[%]'],yerr=l['PLT_SlopeAbsErr[%]'],fmt='o',label = 'lead', color='red')
plt.legend(numpoints=1)
plt.ylabel('$Slope [\% /SBIL]$', fontsize=18)
plt.xlabel('$SBIL [Hz/{\mu b}]$', fontsize=16)
plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
plt.figtext(0.29,0.8,'Preliminary 2017',fontsize=18,style='italic',backgroundcolor='white')
plt.savefig('slope(SBIL).png')
plt.show()


plt.ylim(ymin=-1,ymax=2.7)
plt.errorbar(t.Fill,t['PLT_Slope[%]'],yerr=t['PLT_SlopeAbsErr[%]'],fmt='o',label = 'train')
plt.errorbar(l.Fill,l['PLT_Slope[%]'],yerr=l['PLT_SlopeAbsErr[%]'],fmt='o',label = 'lead', color='red')
plt.legend(numpoints=1)
plt.ylabel('$Slope [\% /SBIL]$', fontsize=18)
plt.xlabel('Fill', fontsize=16)
plt.figtext(0.2,0.8,'CMS',fontsize=18,fontweight='bold',backgroundcolor='white')
plt.figtext(0.29,0.8,'Preliminary 2017',fontsize=18,style='italic',backgroundcolor='white')
plt.savefig('slope(Fill).png')
plt.show()
