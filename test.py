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
central = '/eos/cms/store/group/dpg_bril/comm_bril/vdmdata2017/'
corr = ['BeamBeam','LengthScale','Background']
test = True

for a in os.listdir(central):
    if str.isdigit(str(a[0])) and (int(a[:4]) == 6016):#in [6377,6381,6382,6384,6385]):#6275,6283,
        try:
            t1 = dt.datetime.strptime(a[5:15],'%y%m%d%H%M%S')
            t2 = dt.datetime.strptime(a[-14:-4],'%y%m%d%H%M%S')
            td = t2-t1
            _dg = a != '6016_1707280356_1707280409.hd5'
            print(corr)
            # AutoAnalysis.Analyse(central + a, ['noCorr'], test, post=False, dg=_dg,
            #                      pdfs = False, logs = False)
            AutoAnalysis.Analyse(central + a, corr, test, post=False,
                                 pdfs = True, logs = False)
            # AutoAnalysis.Analyse(central + a, ['Background', 'BeamBeam', 'LengthScale'], test, post=False, dg=_dg,
            #                      pdfs = True, logs = True)
            
            #AutoAnalysis.Analyse(central + a, corr, test, post=False, dg=False, pdfs = True, logs = False)
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            message = 'Error on ' + a + '\n' + traceback.format_exc()
            print(message)
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                + '\n' + message)
            if 'No times' not in message:
                raise KeyboardInterrupt
# h5 = tables.open_file('/brildata/vdmdata17/5730_1705301528_1705301557.hd5')
# vdmscan = pd.DataFrame.from_records(h5.root.vdmscan[:])
# vdmscan = Configurator.RemapVdMDIPData(vdmscan)
# Configurator.GetTimestamps(vdmscan, 5730,'test')