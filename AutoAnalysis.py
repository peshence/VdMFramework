import datetime as dt
import logging
import os
import time
import traceback
import requests
import argparse
import subprocess
import re

import numpy as np
import pandas as pd
import runAnalysis
import tables
import pickle
import json
import Configurator
from postvdm import PostOutput

logging.basicConfig(filename="Automation/Logs/watcher_" +
                            dt.datetime.now().strftime('%y%m%d%H%M%S') + '.log', level=logging.DEBUG)
# luminometers = ['HFLumiET']
# fits = ['SGConst']
# ratetables = ['hfetlumi']
# luminometers = ['PLT0','PLT1','PLT2','PLT3','PLT4','PLT5','PLT6','PLT7','PLT8']
# fits = ['SG','SG','SG','SG','SG','SG','SG','SG','SG']
# ratetables = ['pltlumizero','pltlumizero','pltlumizero','pltlumizero','pltlumizero','pltlumizero','pltlumizero','pltlumizero','pltlumizero']
# luminometers = ['BCM1F', 'HFLumi', 'PLT', 'HFET']
# fits = ['SGConst', 'SGConst', 'SG', 'SGConst']
# ratetables = ['bcm1flumi', 'hfoclumi', 'pltlumizero', 'hfetlumi']
# luminometers = ['PLT','HFLumi', 'BCM1F', 'HFLumiET']
# fits = ['DG', 'DGConst', 'DGConst', 'DGConst']
# ratetables = ['pltlumizero', 'hfoclumi', 'bcm1flumi', 'hfetlumi']
# luminometers = ['PLT','HFLumi', 'BCM1F', 'HFLumiET']
# fits = ['DG', 'DGConst', 'DGConst', 'DGConst']
# ratetables = ['pltlumizero', 'hfoclumi', 'bcm1flumi', 'hfetlumi']

central_default = '/brildata/vdmdata17/'
folder = 'Automation/'


def Analyse(filename, corr, test,filename2 = None, post = True, automation_folder = folder):
    '''Uses vdm data from hd5 file to create configurations for analysis and run them,
        then posts results to web monitor service and saves json dumps of data sent
        
        filename is the name of the hd5 file you're analysing
        corr is the correction you want applied, which is only BeamBeam right now (or noCorr)
        test is a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
        filename2 is the name of the second file of a scan pair for large scans
        post is a boolean that tells if you want your data posted at all (and ouput to json)
        automation_folder is the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders
    '''
    with tables.open_file(filename) as h5:
        if 'vdmscan' not in h5.root:
            print 'no vdmscan table'
            raise Exception('no vdmscan table')
        data = Configurator.RemapVdMDIPData(
            pd.DataFrame.from_records(h5.root.vdmscan[:]))

        ratetables = [i.name for i in h5.root if 'lumi' in i.name]
        
        fill = int(data.loc[0,'fill'])
        run = int(data.loc[0,'run'])
    if filename2:        
        with tables.open_file(filename2) as h5:
            if 'vdmscan' not in h5.root:
                print 'no vdmscan table'
                raise Exception('no vdmscan table')
            data2 = Configurator.RemapVdMDIPData(
                pd.DataFrame.from_records(h5.root.vdmscan[:]))
            filename = os.path.dirname(filename)
        data = data.append(data2, ignore_index = True)
    luminometers = []
    fits = []
    for r in ratetables:
        l = re.match('([a-z1]*)lumi(.*)', r).group(1)#('PLT' if 'plt' == r[:3] else (r[:4] if r[:5] != 'bcm1f' else 'bcm1f'))
        l = l if r != 'hflumi' else 'hfoc'
        if filename2:
            f = ('DG' if 'plt' == r[:3] else 'DGConst')
        else:
            f = ('SG' if 'plt' == r[:3] else 'SGConst')
        if str.isdigit(r[-1]):
            l = l + r[-2:]
        luminometers.append(l.upper())
        fits.append(f)

        
    timestamp = lambda i: dt.datetime.fromtimestamp(
        data.iloc[i]['sec']).strftime('%d%b%y_%H%M%S')
    name = str(fill) + '_' + timestamp(0) + \
                '_' + timestamp(-1)

    times = Configurator.GetTimestamps(data, fill, name, automation_folder=automation_folder)
    if not times or len(times) < 2:
        message = 'No times'
        print message
        logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                            + '\n' + message)
        return

    procs = []
    for i, [luminometer, fit, ratetable] in enumerate(zip(luminometers, fits, ratetables)):
        if ratetable == 'hfoclumi' and fill < 5737:
            ratetable = 'hflumi'
        angle = 0
        if int(fill) > 5737:
            angle = int(data.iloc[0]['xingHmurad'])
            Configurator.ConfigDriver(times, fill, luminometer, fit, ratetable, name, filename, not i, _bstar = int(data.iloc[0]['bstar5'])/100, _angle = angle, automation_folder=automation_folder)
        else:
            Configurator.ConfigDriver(times, fill, luminometer, fit, ratetable, name, filename, not i, automation_folder=automation_folder)
        # fitresults, calibration = runAnalysis.RunAnalysis(name, luminometer, fit, corr, automation_folder=automation_folder)
        if i == 0:
            fitresults, calibration = runAnalysis.RunAnalysis(name, luminometer, fit, corr, automation_folder=automation_folder)
        else:
            # this is done like this because ROOT is being a bitch and I'm in a hurry, it should be doable with the threading module 
            proc = subprocess.Popen(['python', 'runAnalysis.py','-n', name,'-l',luminometer,'-f',fit,'-c',corr,'-a',automation_folder])
            procs.append(proc)
        # if post:
        #     PostOutput(fitresults, calibration, times, fill, run, True if test else False, name, luminometer, fit, angle, corr, automation_folder=folder)
    print len(procs)
    for j,p in enumerate(procs):
        print j
        p.wait()
    if post:
        for i, [luminometer, fit, ratetable] in enumerate(zip(luminometers, fits, ratetables)):
            fitresults = pickle.load(open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer + '/results/BeamBeam/' + fit + '_FitResults.pkl'))
            calibration = pickle.load(open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer + '/results/BeamBeam/LumiCalibration_' + luminometer + '_' + fit + '_' + str(fill) + '.pkl'))
            fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
            calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
            PostOutput(fitresults, calibration, times, fill, run, True if test else False, name, luminometer, fit, angle, corr, automation_folder=folder)
    
    os.system('chmod -R 777 ' + os.getcwd() + '/' + automation_folder + 'Analysed_Data/' + name)

def RunWatcher(corr, test, central = central_default):
    '''Checks folder for new hd5 files, 
        makes configuration files for them and runs analysis, sending the results to an external service
        
        corr is the correction you want applied, which is only BeamBeam right now (or noCorr)
        test is a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
        central is the folder you'll be watching, you should leave it as is
        '''
    
    before = os.listdir(central)
    while True:
        try:
            after = os.listdir(central)
            print after[-10:]
            added = [f for f in after if not f in before]

            for a in added:
                print a
                if a[-4:] == '.hd5':
                    try:
                        Analyse(central + a, corr, test)
                    except (KeyboardInterrupt, SystemExit):
                        raise 
                    except:
                        message = 'Error on ' + a + '\n' + traceback.format_exc()
                        print message
                        logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                         + '\n' + message)
                        message = 'trying to rerun after 10 seconds'
                        print message
                        logging.info('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                         + '\n' + message)
                        time.sleep(10)
                        try:
                            Analyse(central + a, corr, test)
                        except (KeyboardInterrupt, SystemExit):
                            raise 
                        except:
                            message = 'Error on ' + a + '\n' + traceback.format_exc()
                            print message
                            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                         + '\n' + message)
            before = after

        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            message = 'Error on ' + a + '\n' + traceback.format_exc()
            print message
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                            + '\n' + message)
                    
        print 'step' + dt.datetime.now()
        time.sleep(20)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( '-f', '--filename', help='When you need to analyse a single file outside of loop')
    parser.add_argument( '-c', '--central', help='Folder to watch, default is ' + central_default)
    parser.add_argument( '-b', '--beambeam', help='If you want beam beam correction', action='store_true')
    parser.add_argument( '-t', '--test', help='Post to test instead of normal service', action='store_true')
    parser.add_argument( '-p', '--post', help='if you want your one time analysis posted (watcher automatically posts)', action='store_true')
    parser.add_argument( '-f2', '--filename2', help='Second scan of your scan pair')
    parser.add_argument( '-d', '--double', help='Use double gaussians instead of single', action='store_true')
    parser.add_argument( '-r', '--rerun', help='Runs all hd5 file analysis with single gaussians', action='store_true')
    args = parser.parse_args()
    corr = 'noCorr'
    
    config = json.load(open('configAutoAnalysis.json'))
    global luminometers,fits,ratetables
    luminometers = config['luminometers']
    ratetables = config['ratetables']
    fits = config['fits']
    folder = config['automation_folder']

    if args.double:
        fits = config['dfits']
    if args.beambeam:
        corr='BeamBeam'
    if args.filename2:
        Analyse(args.filename, corr, args.test, args.filename2, args.post, automation_folder = folder)
    elif (args.filename):
        Analyse(args.filename, corr, args.test, post = args.post, automation_folder = folder)
    elif (args.central):
        RunWatcher(corr, args.test, args.central)
    elif (args.rerun):
        for i in os.listdir(central_default):
            if i[-4:]=='.hd5':# and int(i[:4]) > 5746:
                try:
                    Analyse(central_default+i,corr,args.test, post = args.post, automation_folder = folder)
                except (KeyboardInterrupt, SystemExit):
                    raise 
                except:
                    message = 'Error on ' + i + '\n' + traceback.format_exc()
                    print message
                    logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 
                                + '\n' + message)
    else:
        RunWatcher(corr, args.test)