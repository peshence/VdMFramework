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


def RunAnalysis(name, luminometer, fit, corr = 'noCorr', automation_folder = 'Automation/'):
    """Runs vdm driver without correction and with beam beam correction,
        then calculates the calibration constant ant plots the results in pdfs
        You need to have already made the configuration files in automation_folder + '/autoconfigs'
        
        name is the name of the analysis folder (fill number and datetimes from the beginning and ending of the scan pair)
        automation_folder is the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders
        """
    def LogInfo(message):
        print(message)
        logging.info('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') +
                      '\n\tFile ' + name + '\n\t' + message)
    try:
        LogInfo('NO CORR ' + luminometer + fit + ' START')
        fitresults = vdmDriverII.DriveVdm(automation_folder + 'autoconfigs/' + name + '/' +
                             luminometer + 'noCorr_' + fit + '_driver.json')  
        if corr != 'noCorr':
            LogInfo(corr + ' ' + luminometer + fit + ' START')    
            fitresults = vdmDriverII.DriveVdm(automation_folder + 'autoconfigs/' + name + '/' +
                                luminometer + corr + '_' + fit + '_driver.json')
                             
        LogInfo('CALIBRATION CONST ' + luminometer + fit + ' START')
        calibration = calculateCalibrationConstant.CalculateCalibrationConstant(
            automation_folder + 'autoconfigs/' + name + '/' + luminometer + corr + '_' + fit + '_calibrationConst.json')
        
        LogInfo('PLOT FIT ' + luminometer + fit + ' START')
        plotFitResults.PlotFit(automation_folder + 'autoconfigs/' + name + '/' +
                               luminometer + corr + '_' + fit + '_plotFit.json')    
        config = json.load(open(automation_folder + 'autoconfigs/' + name + '/' +
                             luminometer + 'noCorr_' + fit + '_driver.json'))
        fill = config['Fill']
        time = config['makeScanFileConfig']['ScanTimeWindows'][0][0]
        fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
        calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
        #LogInfo(luminometer + fit + ' END')
        return fitresults, calibration

    except (KeyboardInterrupt, SystemExit):
        raise 
    except:
        message = 'Error analysing data!\n' + traceback.format_exc()
        print message
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
    logging.basicConfig(filename=args.automation_folder + "Logs/run_" + args.luminometer + '.log', level=logging.DEBUG)
    logging.info('name' + args.name)
    logging.info('luminometer' + args.luminometer)
    logging.info('fit' + args.fit)
    logging.info('corr' + args.corr)
    logging.info('automation_folder' + args.automation_folder)
    
    RunAnalysis(args.name,args.luminometer,args.fit,args.corr,args.automation_folder)
### OLD
# '''THIS MAY NOT BE WORKING'''
# #and that's ok, you don't need it
# if (__name__ == '__main__'):
#     """Analyse data for fill with premade configuration,
#         - default runs through luminometers with SG and SGconst fits
#         - you can choose single luminometer and fit funciton
#         - default posts to test""" 
#     luminometers = ['PLT', 'BCM1F', 'HFLumi', 'HFLumiET']
#     fits = ['SG', 'SGConst', 'SGConst', 'SGConst']
#     dfits = ['DG', 'DGConst', 'DGConst', 'DGConst']
#     endpoint = None
#     logging.basicConfig(filename="Logs/run_" + dt.datetime.now().strftime(
#         '%y%m%d%H%M%S') + '.log', level=logging.DEBUG)
#     parser = argparse.ArgumentParser()
    
#     parser.add_argument('-d', '--double', help='Fit with double Gaussians')
#     parser.add_argument('-l', '--luminometer', help='you should also provide a fit function with this')
#     parser.add_argument('-fit', '--fitfunction', help='you should also provide a luminometer with this')
#     parser.add_argument('-c', '--correction', help='currently only BeamBeam and noCorr are possible')                    
#     parser.add_argument('-f', '--file', help='File you want analysed')
#     parser.add_argument('--fill', help='Number of fill you want analysed (old data or single scan fills)')
    
#     args = parser.parse_args()

#     if args.fill:
#         FillNum = args.fill
#         configfolders = os.listdir('autoconfigs/')
#         name = FillNum
#         for config in configfolders:
#             if config[:4] == str(FillNum):
#                 name = config
#                 break
#     else:
#         name = args.file
#     corr = 'noCorr'
#     if args.correction:
#         corr = args.correction
    
#     if args.fitfunction:
#         RunAnalysis(name, args.luminometer, args.fitfunction, corr)
#     elif args.double:
#         print luminometers, '\n', dfits, '\nYou sure?'
#         for lumi, fit in zip(luminometers,dfits):
#             RunAnalysis(name,lumi,fit,corr)
#     else:
#         print luminometers, '\n', fits, '\nYou sure?'
#         for lumi, fit in zip(luminometers,fits):
#             RunAnalysis(name,lumi,fit,corr)
