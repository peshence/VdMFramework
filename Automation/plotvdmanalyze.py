import VdManalyze as v
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse as ap

start,end = 6075,6115
lumis = ['PLT','HFET', 'HFOC', 'BCM1FPCVD']
# df = v.load_all(['PLT'],6300,6372
parser = ap.ArgumentParser()
parser.add_argument('-s', '--start')
parser.add_argument('-e', '--end')
parser.add_argument('-l', '--lumis')
args = parser.parse_args()
if args.start:
    start = args.start
if args.end:
    end = args.end
if args.lumis:
    lumis = args.lumis
def round_to_sign(x):
    return round(x, -int(np.floor(np.log10(abs(x))))+1)

def plotfit(x,y,sigma):
    print sigma
    (a,b), cov = np.polyfit(x, y, 1, w=[(1/i if i else 1/np.mean(sigma)) for i in sigma], cov=True)
    mean = np.mean(y)
    la,lb = a,b
    la = la/mean*100
    cov[0][0] = cov[0][0]/mean*100
    lae = round_to_sign(cov[0][0])
    lbe = round_to_sign(cov[1][1])
    la = round(la,len(str(lae)) - '{0:f}'.format(lae).index('.') - 1)
    lb = round(lb,len(str(lbe)) - '{0:f}'.format(lbe).index('.') - 1)
    plt.plot(x, [a*i + b for i in x], label = '(' + str(la) + '$\pm$' + str(lae) + ')%x + ' + str(lb) + '$\pm$' + str(lbe)  )  


def main(start,end,lumis):
    ldf = v.load_all(lumis, start, end, leading=True)
    tdf = v.load_all(lumis, start, end, train=True)
    ldf.to_csv('leading_' + str(start) + '-' + str(end) + '.csv')
    tdf.to_csv('train_' + str(start) + '-' + str(end) + '.csv')


    for lumi in lumis: 
        
        ldfc = ldf.loc[[not np.isnan(i) for i in ldf[lumi + '_sigmavis']]]
        tdfc = tdf.loc[[not np.isnan(i) for i in tdf[lumi + '_sigmavis']]]

        terr = [i if i else 1/np.mean(tdfc[lumi + '_sigmavis_err']) for i in tdfc[lumi + '_sigmavis_err']]
        lerr = [i if i else 1/np.mean(ldfc[lumi + '_sigmavis_err']) for i in ldfc[lumi + '_sigmavis_err']]
        plt.errorbar(tdfc[lumi + '_SBIL'].tolist(),tdfc[lumi + '_sigmavis'].tolist(),yerr=tdfc[lumi + '_sigmavis_err'].tolist(),fmt='o',label='Train')
        plt.errorbar(ldfc[lumi + '_SBIL'].tolist(),ldfc[lumi + '_sigmavis'].tolist(),yerr=ldfc[lumi + '_sigmavis_err'].tolist(),fmt='o',label='Leading')

        plotfit(tdfc[lumi + '_SBIL'].tolist(),tdfc[lumi + '_sigmavis'].tolist(),terr)
        plotfit(ldfc[lumi + '_SBIL'].tolist(),ldfc[lumi + '_sigmavis'].tolist(),lerr)
        plt.legend()
        plt.title(lumi + ' $\sigma_{vis}$ average per fill for fills ' + str(start) + '-' + str(end))
        plt.ylabel('$\sigma_{vis}$ $\mu b$')
        plt.xlabel('SBIL')
        plt.savefig(lumi + '_' + str(start) + '-' + str(end) + '.png')
        plt.show()

main(start,end,lumis)