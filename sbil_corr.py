import runAnalysis
import pickle
import pandas as pd
import json
import Configurator
import os
import MiniScanAnalysis
import logging
import traceback
import datetime as dt

import tables

central = '/brildata/vdmdata17/'
corr = 'BeamBeam'
test = True
folder = 'Automation/'
lumi = 'PLT'
fit = 'SG'
ratetable = 'pltlumizero'


if os.getcwd()[-4:] == 'Test':
    folder = '../' + folder
for a in os.listdir(central):
    if a[0] != 'b' and int(a[:4])==5848:
        try:
            MiniScanAnalysis.Analyse(central + a, corr, test, post=False,analysis_folder=folder)
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            message = 'Error on ' + a + '\n' + traceback.format_exc()
            print message
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                + '\n' + message)
            input()