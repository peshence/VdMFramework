import runAnalysis
import pickle
import pandas as pd
import json
import Configurator
import os
import AutoAnalysis
import logging
import traceback
import datetime as dt
from multiprocessing.dummy import Pool

import tables
central = '/brildata/vdmdata17/'
corr = 'BeamBeam'
test = True
folder = 'Automation/'

def do(a):
    print a
    if str.isdigit(str(a[0])) and (int(a[:4]) in [6016,6362]):#6275,6283,
        try:
            t1 = dt.datetime.strptime(a[5:15],'%y%m%d%H%M%S')
            t2 = dt.datetime.strptime(a[-14:-4],'%y%m%d%H%M%S')
            td = t2-t1
            _dg = td.total_seconds() > 600
            for i in range(-5,6):
                AutoAnalysis.Analyse(central + a, corr, test, post=False, eff = i*1.0, dg= int(a[:4])==6016, pdfs = True, logs = False)
            
            #AutoAnalysis.Analyse(central + a, corr, test, post=False, dg=False, pdfs = True, logs = False)
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            message = 'Error on ' + a + '\n' + traceback.format_exc()
            print message
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                + '\n' + message)
# h5 = tables.open_file('/brildata/vdmdata17/5730_1705301528_1705301557.hd5')
# vdmscan = pd.DataFrame.from_records(h5.root.vdmscan[:])
# vdmscan = Configurator.RemapVdMDIPData(vdmscan)
# Configurator.GetTimestamps(vdmscan, 5730,'test')

if os.getcwd()[-4:] == 'Test':
    global folder
    folder = '../' + folder
ts=[]
pool = Pool(8)
pool.map(do, [a for a in os.listdir(central) if str.isdigit(str(a[0])) and (int(a[:4]) in [6016,6362])])
pool.close()
pool.join()
