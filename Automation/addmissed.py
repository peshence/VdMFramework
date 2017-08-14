import requests
import argparse
import os
import json
import re
import datetime as dt

"luminometers": ["PLT", "HFET", "HFOC", "BCM1FSI", "BCM1FPCVD", "BCM1FSCVD"],
"fits": ["SG", "SGConst","SGConst","SGConst","SGConst","SGConst"],
"dfits": ["DG","DGConst","DGConst","DGConst","DGConst","DGConst"],
"ratetables": ["pltlumizero", "hfetlumi", "hfoclumi", "bcm1fsilumi", "bcm1fpcvdlumi", "bcm1fscvdlumi"]

def repost(folder):
    t1 = dt.datetime.strptime(folder[-30:-16],'%d%b%y_%H%M%S')
    t2 = dt.datetime.strptime(folder[-15:-1],'%d%b%y_%H%M%S')
    td = t2-t1
    fit = 'SG' if td.total_seconds() <= 600 else 'DG'
    jsons = [i for i in os.listdir(folder) if fit in i]
    for i, [luminometer, fit, ratetable] in enumerate(zip(luminometers, fits, ratetables)):
        try:
            fitresults = pickle.load(open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer + '/results/BeamBeam/' + fit + '_FitResults.pkl'))
            calibration = pickle.load(open(automation_folder + 'Analysed_Data/' + name + '/' + luminometer + '/results/BeamBeam/LumiCalibration_' + luminometer + '_' + fit + '_' + str(fill) + '.pkl'))
            fitresults = pd.DataFrame(fitresults[1:], columns=fitresults[0])
            calibration = pd.DataFrame(calibration[1:], columns=calibration[0])
            PostOutput(fitresults, calibration, times, fill, run, True if test else False, name, luminometer, fit, angle, corr, automation_folder=folder)
        except (KeyboardInterrupt, SystemExit):
            raise 
        except:
            message = 'Couldnt post ' + luminometer + '\n' + traceback.format_exc()
            print message
            logging.error('\n\t' + dt.datetime.now().strftime('%y%m%d%H%M%S') 

if args.file:
    repost(args.file)
else:
    for f in os.listdir('Analysed_Data/'):
        if f[0] != 'F':# and int(f[:4])>5965) and int(f[:4])<5980) : #f == '6016_28Jul17_100004_28Jul17_112346':
            print 'yes'
            repost('Analysed_Data/' + f + '/')