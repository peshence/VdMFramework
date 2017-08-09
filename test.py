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

import tables
central = '/brildata/vdmdata17/'
corr = 'BeamBeam'
test = True
folder = 'Automation/'

if os.getcwd()[-4:] == 'Test':
    global folder
    folder = '../' + folder
for a in os.listdir(central):
    if str.isdigit(str(a[0])) and int(a[:4])>6035:#>5940 and int(a[:4])<5980:
        try:
            AutoAnalysis.Analyse(central + a, corr, test, post=True, dg=False)
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