import argparse
import datetime as dt
import json
import logging
import os
import sys
import traceback

import numpy as np
import pandas as pd
import requests

import calculateCalibrationConstant
import Configurator
import Scripts.plotFitResults as plotFitResults
import vdmDriverII
from postvdm import PostOutput


def RunAnalysis(name, luminometer, fit, corr='noCorr', automation_folder='Automation/'):
    """Runs vdm driver without correction and with beam beam correction,
        then calculates the calibration constant ant plots the results in pdfs
        You need to have already made the configuration files in automation_folder + '/autoconfigs'

        name : the name of the analysis folder (fill number and datetimes from the beginning and ending of the scan pair)
        automation_folder : the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders
        """
    def LogInfo(message):
        print(message)
        logging.info('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') +
                     '\n\tFile ' + name + '\n\t' + message)
    try:
        beambeamsource = 'noCorr_' if 'Background' not in corr else 'Background_'
        if 'BeamBeam' in corr:
            # LogInfo(beambeamsource + ' ' + luminometer + fit + ' START')
            fitresults,calibration = vdmDriverII.DriveVdm(automation_folder + 'autoconfigs/' + name + '/' +
                                            luminometer + beambeamsource + fit + '_driver.json')

            # LogInfo('CALIBRATION CONST ' + luminometer + fit + ' START')
            # calibration = calculateCalibrationConstant.CalculateCalibrationConstant(
            #     automation_folder + 'autoconfigs/' + name + '/' + luminometer + beambeamsource + fit + '_calibrationConst.json')
        
        # LogInfo(corr + ' ' + luminometer + fit + ' START')
        fitresults,calibration = vdmDriverII.DriveVdm(automation_folder + 'autoconfigs/' + name + '/' +
                                            luminometer + corr + '_' + fit + '_driver.json')

        # LogInfo('CALIBRATION CONST ' + luminometer + fit + ' START')
        # calibration = calculateCalibrationConstant.CalculateCalibrationConstant(
        #     automation_folder + 'autoconfigs/' + name + '/' + luminometer + corr + '_' + fit + '_calibrationConst.json')

        # these just take up space in emittance scans. If you need them the configurations are still made
        # LogInfo('PLOT FIT ' + luminometer + fit + ' START')
        # plotFitResults.PlotFit(automation_folder + 'autoconfigs/' + name + '/' +
        #                        luminometer + corr + '_' + fit + '_plotFit.json')

        config = json.load(open(automation_folder + 'autoconfigs/' + name + '/' +
                                luminometer + beambeamsource + fit + '_driver.json'))
        fill = config['Fill']
        time = config['makeScanFileConfig']['ScanTimeWindows'][0][0]
        fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
        calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
        #LogInfo(luminometer + fit + ' END')
        return fitresults, calibration

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        raise
        message = 'Error analysing data!\n' + traceback.format_exc()
        print(message)
        logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') +
                      '\n\tFile ' + name + '\n' + message)


if (__name__ == '__main__'):
    '''Should just be the above method runnable from console, but is not tested'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', help='name of new analysis folder')
    parser.add_argument('-l', '--luminometer')
    parser.add_argument('-f', '--fit')
    parser.add_argument('-c', '--corr')
    parser.add_argument('-a', '--automation_folder')
    args = parser.parse_args()
    # if not os.path.exists(args.automation_folder + '/Analysed_Data/' + args.name + '/Logs/'):
    #     os.makedirs(args.automation_folder + '/Analysed_Data/' + args.name + '/Logs/')
    # logging.basicConfig(filename=args.automation_folder + '/Analysed_Data/' + args.name +
    #                     "/Logs/run_" + args.luminometer + '.log', level=logging.DEBUG)
    # logging.info('name: ' + args.name)
    # logging.info('luminometer: ' + args.luminometer)
    # logging.info('fit: ' + args.fit)
    # logging.info('corr: ' + args.corr)
    # logging.info('automation_folder: ' + args.automation_folder)

    RunAnalysis(args.name, args.luminometer, args.fit,
                args.corr, args.automation_folder)
