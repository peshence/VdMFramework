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
import tables
import pickle
import json
import Configurator
from postvdm import PostOutput


central_default = '/brildata/vdmdata17/'
folder = 'Automation/'
config = json.load(open('configAutoAnalysis.json'))

_ratetables = config['ratetables']
folder = os.path.relpath(config['automation_folder']) + '/'
central_default =  os.path.relpath(config['central_default']) + '/'
log_folder = config['log_folder'] + '/'
max_threads = config['max_threads']
dg_steps = config['dg_steps']

if not os.path.exists(log_folder):
    os.makedirs(log_folder)
logging.basicConfig(filename= log_folder + 'VdM_' +
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.log', level=logging.INFO)
# requests module gives unnecessary info and debug logs
logging.getLogger("requests").setLevel(logging.WARNING)

if not os.path.exists('./' + folder):
    os.mkdir('./' + folder)
subfolders = ['Analysed_Data/', 'dipfiles/', 'autoconfigs/']
for subfolder in subfolders:
    if not os.path.exists('./' + folder + subfolder):
        os.mkdir('./' + folder + subfolder)


def Analyse(filename, corr, test, filename2=None, post=True, automation_folder=folder, dg=False, logs = False, pdfs = False):
    '''Uses vdm data from hd5 file to create configurations for analysis and run them,
        then posts results to web monitor service and saves json dumps of data sent

        filename : the name of the hd5 file you're analysing
        corr : the correction you want applied, which is only BeamBeam right now (or noCorr)
        test : a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
        filename2 : the name of the second file of a scan pair for large scans
        post : a boolean that tells if you want your data posted at all (and ouput to json)
        automation_folder : the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders
    '''
    with tables.open_file(filename) as h5:
        if 'vdmscan' not in h5.root:
            print('no vdmscan table')
            raise Exception('no vdmscan table')
        data = Configurator.RemapVdMDIPData(pd.DataFrame.from_records(h5.root.vdmscan[:]))

        ratetables = [i.name for i in h5.root if 'lumi' in i.name and i.name != 'pltslinklumi'
                                                                and i.name != 'luminousregion']

        fill = int(data.loc[0, 'fill'])
        run = int(data.loc[0, 'run'])
    if filename2:
        with tables.open_file(filename2) as h5:
            if 'vdmscan' not in h5.root:
                print('no vdmscan table')
                raise Exception('no vdmscan table')
            data2 = Configurator.RemapVdMDIPData(pd.DataFrame.from_records(h5.root.vdmscan[:]))
            filename = os.path.dirname(filename)
        data = data.append(data2, ignore_index=True)

    def timestamp(i): return dt.datetime.fromtimestamp(data.iloc[i]['sec']).strftime('%d%b%y_%H%M%S')
    dip = automation_folder + 'dipfiles/dip_' + str(fill) + '_' + timestamp(0)\
          + '_' + timestamp(-1) + '.csv'
    data.to_csv(dip)

    alltimes, allsteps = Configurator.GetTimestamps(data, fill, automation_folder=automation_folder)
    if not alltimes:
        raise Exception('No times')
    if len(alltimes) < 2:
        raise Exception('Not a scan pair')

    for scanpair in xrange(0, len(alltimes), 2):
        # get timestamps and number of steps for each scan        
        times = alltimes[scanpair:scanpair + 2]
        steps = allsteps[scanpair:scanpair + 2]
        scantimes = Configurator.FormatTimestamps(times)[-1]

        # make ratetable-luminometername-fit tuples
        luminometers = []
        fits = []
        if test:
            ratetables = _ratetables
        for r in ratetables:
            l = re.match('([a-z1]*)_?lumi(.*)', r).group(1)
            l = l if r != 'hflumi' else 'hfoc'
            if dg or filename2 or steps[0]>dg_steps:
                # f = ('DG' if 'plt' == r[:3] else 'DGConst')
                #f = ('DG' if 'plt' == r[:3] or 'bcm1f'==r[:5] else 'DGConst')
                f= 'DG'
            else:
                f = 'SG'
                # f = ('SG' if 'plt' == r[:3] else 'SGConst')
                # f = ('SG' if 'plt' == r[:3] or 'bcm1f'==r[:5] else 'SGConst')
            if str.isdigit(str(r[-1])):
                if str.isdigit(str(r[-2])):
                    l = l + r[-2:]
                else:
                    l = l + r[-1]
            luminometers.append(l.upper())
            fits.append(f)
        
        # Create a time-based name for this scan
        def ts(i): return dt.datetime.fromtimestamp(i).strftime('%d%b%y_%H%M%S')
        name = str(fill) + '_' + ts(times[0][0][0]) + '_' + ts(times[1][0][0])

        threads = zip(luminometers, fits, ratetables)
        angle = 0
        for i, (luminometer, fit, ratetable) in enumerate(threads):
                if ratetable == 'hfoclumi' and fill < 5737:
                    ratetable = 'hflumi'
                if int(fill) > 5737:
                    angle = int(data.iloc[data[data.sec==times[0][0][0]].index[0]]['xingHmurad'])
                    Configurator.ConfigDriver(times, fill, luminometer, fit, ratetable, name,
                        filename, corr=corr, _bstar=float(data.iloc[0]['bstar5']) / 100,
                        _angle=angle, dip=dip, automation_folder=automation_folder,
                        autoconfigs_folder='Automation/', makepdf = pdfs, makelogs=logs)
                else:
                    if ratetable == 'hfoclumi': ratetable = 'hflumi'
                    Configurator.ConfigDriver(times, fill, luminometer, fit, ratetable, name,
                                filename, corr=corr, dip=dip, automation_folder=automation_folder,
                                autoconfigs_folder='Automation/', makepdf = pdfs, makelogs=logs)
        
        # run one luminometer to get common files made
        # (otherwise all processes will try to make them at the same time)
        _corr = reduce(lambda a,b: str(a) + '_' + str(b), corr)
        luminometer = luminometers[0]
        fit = fits[0]
        try:
            proc = subprocess.Popen(['python', 'runAnalysis.py', '-n', name, '-l', luminometer, '-f',
                                    fit, '-c', reduce(lambda a,b: str(a) + '_' + str(b), corr), '-a',
                                    automation_folder], stderr=subprocess.PIPE)
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            raise KeyboardInterrupt
        if proc.returncode: # this is 0 if the process didn't have any errors
            print(proc.stderr.read())
            logging.error(str.format('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S'),
                          luminometer + ' ' + fit + '\n' + proc.stderr.read()))
            # even if it fails, it should have done the common parts (scan file,beam currents file)
            # TODO implement per script errors to have a better grip on what happened
            
        else:
            with open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer + 
                      '/results/'+ _corr + '/' + fit + '_FitResults.pkl') as fr:
                      fitresults = pickle.load(fr)
            with open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer +
                      '/results/'+ _corr + '/LumiCalibration_' + luminometer + '_' + fit
                      + '_' + str(fill) + '.pkl') as cal: calibration = pickle.load(cal)

            fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
            calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
            if str.isdigit(str(luminometer[-1])):
                PostOutput(fitresults, calibration, scantimes, fill, run, False, name, luminometer,
                        fit, angle, _corr, automation_folder=automation_folder, post=post, perchannel=True)
            if ratetable in _ratetables:
                PostOutput(fitresults, calibration, scantimes, fill, run, False, name, luminometer,
                            fit, angle, _corr, automation_folder=automation_folder, post=post)
        for k in xrange(1, len(threads), max_threads):
            procs = []
            try:
                for i, (luminometer, fit, ratetable) in enumerate(threads[k:k + max_threads]):
                    proc = subprocess.Popen(['python', 'runAnalysis.py', '-n', name, '-l', luminometer,
                                            '-f', fit, '-c', reduce(lambda a,b: str(a) + '_' + str(b),
                                            corr), '-a', automation_folder],stderr=subprocess.PIPE)
                    procs.append(proc)
                
                print('\nRunning ' + str(len(procs)) + ' processes')
                for j, p in enumerate(procs):
                    p.wait()
                    print('Process ' + str(j) + ' finished')
                    if proc.returncode: # this is 0 if the process didn't have any errors
                        print(proc.stderr.read())
                        logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S'),
                                    luminometer + ' ' + fit + '\n' + proc.stderr.read())
            except KeyboardInterrupt:
                for p in procs:
                    p.kill()
                raise KeyboardInterrupt
            
            print('\nStarting to create post-ready jsons')
            if post: print('and posting them')
            for i, (luminometer, fit, ratetable) in enumerate(threads[k:k + max_threads]):
                try:
                    with open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer +
                              '/results/'+ _corr + '/' + fit + '_FitResults.pkl') as fr:
                        fitresults = pickle.load(fr)
                    with open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer +
                              '/results/'+ _corr + '/LumiCalibration_' + luminometer + '_' + fit
                              + '_' + str(fill) + '.pkl') as cal:
                        calibration = pickle.load(cal)
                    fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
                    calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
                    if str.isdigit(str(ratetable[-1])):
                        PostOutput(fitresults, calibration, scantimes, fill, run, False, name, luminometer,
                                fit, angle, _corr, automation_folder=automation_folder, post=post, perchannel=True)
                    elif ratetable in _ratetables:
                        PostOutput(fitresults, calibration, scantimes, fill, run, False, name, luminometer,
                                    fit, angle, _corr, automation_folder=automation_folder, post=post)
                    else:
                        PostOutput(fitresults, calibration, scantimes, fill, run, True, name, luminometer,
                                    fit, angle, _corr, automation_folder=automation_folder, post=post)
                    
                except (KeyboardInterrupt, SystemExit):
                    raise SystemExit
                except:
                    message = 'Couldnt post ' + luminometer + '\n' + traceback.format_exc()
                    print(message)
                    logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S')
                                    + '\n' + message)
            print('\nJSONs created')
            if post: print('and posted.')
        os.system('chmod -R 777 ' + os.getcwd() + '/' +
                  automation_folder + 'Analysed_Data/' + name)
        print('Finished analysing!')


def RunWatcher(corr, test, central=central_default):
    '''Checks folder for new hd5 files, 
        makes configuration files for them and runs analysis, sending the results to an external service

        corr : the correction you want applied, which is only BeamBeam right now (or noCorr)
        test : a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
        central : the folder you'll be watching, you should leave it as is
        '''

    before = os.listdir(central)
    while True:
        try:
            after = os.listdir(central)
            # print(after[-10:])
            added = [f for f in after if not f in before]

            for a in added:
                print('New file: ' + a)
                if a[-4:] == '.hd5':
                    try:
                        Analyse(central + a, corr, test)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        message = 'Error on ' + a + '\n' + traceback.format_exc()
                        print(message)
                        logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S')
                                      + '\n' + message)
                        message = 'trying to rerun after 60 seconds'
                        print(message)
                        logging.info('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S')
                                     + '\n' + message)
                        time.sleep(60)
                        try:
                            Analyse(central + a, corr, test)
                        except (KeyboardInterrupt, SystemExit):
                            raise
                        except:
                            message = 'Error on ' + a + '\n' + traceback.format_exc()
                            print(message)
                            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S')
                                          + '\n' + message)
            before = after

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            message = 'Error on ' + a + '\n' + traceback.format_exc()
            print(message)
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S')
                          + '\n' + message)

        print('step ' + str(dt.datetime.now()))
        time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--filename', help='When you need to analyse a single file outside of loop')
    parser.add_argument('-c', '--central',
                        help='Folder to watch, default is ' + central_default)
    parser.add_argument(
        '-b', '--beambeam', help='If you want beam beam correction', action='store_true')
    parser.add_argument(
        '-t', '--test', help='Only use the luminometers from the config file', action='store_true')
    parser.add_argument('-p', '--post', help='if you want your one time analysis \
                                        posted (watcher automatically posts)', action='store_true')
    parser.add_argument('-f2', '--filename2',
                        help='Second scan of your scan pair')
    parser.add_argument(
        '-d', '--double', help='Use double gaussians instead of single', action='store_true')
    parser.add_argument('-pdf', '--pdfs',
        help='Make pdfs with beam beam corrections and fitted functions', action='store_true')
    parser.add_argument(
        '-l', '--logs', help='Make logs for the fitting (no minuit yet)', action='store_true')
    parser.add_argument(
        '-ls', '--lscale', help='Add length scale correction', action='store_true')
    parser.add_argument(
        '-bg', '--background', help='Add background correction', action='store_true')
    args = parser.parse_args()
    corr = ['noCorr']

    if args.beambeam:
        corr = ['BeamBeam']
    if args.background:
        corr.append('Background')
    if args.lscale:
        corr.append('LengthScale')
    if args.filename2:
        Analyse(args.filename, corr, args.test, args.filename2,
                args.post, automation_folder=folder, pdfs=args.pdfs, logs=args.logs)
    elif (args.filename):
        Analyse(args.filename, corr, args.test, post=args.post,
                automation_folder=folder, dg=args.double, pdfs=True if args.pdfs else False,
                logs=True if args.logs else False)
    elif (args.central):
        RunWatcher(corr, args.test, args.central)
    else:
        RunWatcher(corr, args.test)
