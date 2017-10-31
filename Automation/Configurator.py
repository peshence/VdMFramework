import argparse
import datetime as dt
import json
import logging
import os
import traceback

import numpy as np
import pandas as pd

luminometers = ['PLT', 'HFLumi', 'BCM1F', 'HFLumiET']
fits = ['SG', 'SGConst', 'SGConst', 'SGConst']
ratetables = ['pltlumizero', 'hflumi', 'bcm1flumi', 'hfetlumi']


def GetTimestamps(data, fillnum, name, automation_folder='Automation/'):
    """Gets the VdM scan start and end rows from a DIP 
        VdM dataframe and returns them in pairs like 
        [ (timestamp, nominal_separation_plane), (timestamp, nominal_separation_plane) ] 
        (beginning end end of scan respectively)
        Saves a new reduced vdm file as automation_folder + 'dipfiles/vdm_' + name + '.csv'

        data : the data from a vdm dip csv file or vdmscan table of hd5 files remapped by RemapVdMDIPData
        name : the name of the analysed data folder (fill_datestart_timestart_dateend_timend usually)
        automation_folder : the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders
     """
    # Get cms data for fill
    _dip = automation_folder + 'dipfiles/vdm_' + name + '.csv'
    data = data[(data.ip == 32) & (data.fill == fillnum) & (data.scanstatus == 'ACQUIRING')]
    if 'nominal_separation_plane' in data:
        data = data[(data.nominal_separation_plane != 'NONE')]
    if data.shape[0] == 0:
        message = '\n\t' + 'No data for fill ' + str(fillnum)
        print(message)
        logging.warning('\n\t' + dt.datetime.now().strftime(
            '%d %b %Y %H:%M:%S\n') + message)
        return False

    # Save new dip file for analysis
    data.to_csv(_dip, index=False)
    data = pd.read_csv(_dip) # I realize this is ridiculous, but it doesn't work otherwise, I don't get it either

    # Get start and end rows
                        # (data.nominal_separation_plane != data.shift(1).nominal_separation_plane) |
                        #    (data.nominal_separation_plane != data.shift(-1).nominal_separation_plane) |
                           
    timestamp_data = data[((data.plane != data.shift(-1).plane) | (data.plane != data.shift(1).plane) |
                        (data.nominal_separation_plane != data.shift(1).nominal_separation_plane) |
                        (data.nominal_separation_plane != data.shift(-1).nominal_separation_plane) |
                        (data.step - data.shift(1).step < 0) | (data.shift(-1).step - data.step < 0))]  # .loc[:,['fill','sec','plane','nominal_separation_plane']]
                           
    print timestamp_data.loc[:, ['fill', 'sec', 'plane', 'nominal_separation_plane']]
    logging.info('Timestamps (that look like beginnings and endings of scans):\n' + 
                 str(timestamp_data.loc[:, ['fill', 'sec', 'plane', 'nominal_separation_plane']]))
    # Remove rows with timestamps which don't look like scans and sort the
    # rest into pairs (each pair is a scan)
    for t1, t2 in zip(timestamp_data.index[::2], timestamp_data.index[1::2]):
        # Something happened during VdM that made this think there were multiple super small scans, so I added this
        if t2 - t1 < 30:
            timestamp_data = timestamp_data[(
                timestamp_data.index != t1) & (timestamp_data.index != t2)]
            message = '\n\t' + 'Timestamps ' + str(data.get_value(t1, 'sec')) + ' and ' + str(data.get_value(
                t2, 'sec')) + ' removed due to scan under 30 seconds'
            print message
            logging.warning('\n\t' + dt.datetime.now().strftime(
                '%d %b %Y %H:%M:%S\n') + message)
            continue
        # Scan should finish progress, and it goes down from a certain max
        # number to 1, we don't get data for each but we should always get
        # at least last 3
        if data.get_value(t2, 'progress') > 3:
            timestamp_data = timestamp_data[(
                timestamp_data.index != t1) & (timestamp_data.index != t2)]
            message = '\n\t' + 'Timestamps ' + str(data.get_value(t1, 'sec')) + ' and ' + str(data.get_value(
                t2, 'sec')) + ' removed due to unfinished scan'
            print message
            logging.warning('\n\t' + dt.datetime.now().strftime(
                '%d %b %Y %H:%M:%S\n') + message)
            continue
        if data.get_value(t2, 'step') < 13:
            timestamp_data = timestamp_data[(
                timestamp_data.index != t1) & (timestamp_data.index != t2)]
            message = '\n\t' + 'Timestamps ' + str(data.get_value(t1, 'sec')) + ' and ' + str(data.get_value(
                t2, 'sec')) + ' removed due to steps less then 13'
            print message
            logging.warning('\n\t' + dt.datetime.now().strftime(
                '%d %b %Y %H:%M:%S\n') + message)
            continue
        nom_seps = data.loc[t1:t2, ['nominal_separation', 'sec']]
        nom_seps = nom_seps[nom_seps.nominal_separation !=
                            nom_seps.shift(-1).nominal_separation].copy()
        print nom_seps
        # Constant nominal separation is not a scan
        if nom_seps.empty:
            message = '\n\t' + 'Timestamps ' + str(data.get_value(t1, 'sec')) + ' and ' + str(data.get_value(
                t2, 'sec')) + ' removed due to constant nominal separation'
            print message
            logging.warning('\n\t' + dt.datetime.now().strftime(
                '%d %b %Y %H:%M:%S\n') + message)
            timestamp_data = timestamp_data[(
                timestamp_data.index != t1) & (timestamp_data.index != t2)]
            continue
        # A scan's nominal separation in time should be a monotonous
        # function: every step makes it larger(smaller) as it goes from -A
        # (+A) to +A (-A)
        diffsigns = np.sign(nom_seps.nominal_separation -
                            nom_seps.shift(1).nominal_separation)
        for i in range(len(diffsigns))[2:]:
            if (diffsigns.iloc[i] != diffsigns.iloc[i - 1]):
                # Remove the last step if it was back to top
                if (i == (len(diffsigns) - 1)) & (nom_seps.iloc[i].nominal_separation < 0.0001):
                    # We only really care about the seconds and the plane,
                    # which should be the same but I need to keep the index
                    # up to this point, so no reason to cut the other
                    # columns
                    print int(nom_seps.iloc[i - 1].sec)
                    print int(timestamp_data.get_value(
                        t2, 'sec'))
                    timestamp_data.set_value(
                        t2, 'sec', nom_seps.iloc[i - 1].sec)
                    continue
                message = '\n\t' + 'Timestamps ' + str(data.get_value(t1, 'sec')) + ' and ' + str(data.get_value(
                    t2, 'sec')) + ' removed due to non monotonous nominal separation in time'
                print message
                logging.warning('\n\t' + dt.datetime.now().strftime(
                    '%d %b %Y %H:%M:%S\n') + message)
                timestamp_data = timestamp_data[(
                    timestamp_data.index != t1) & (timestamp_data.index != t2)]
                break
    if 'nominal_separation_plane' in timestamp_data:
        timestamp_data = map(lambda c, d: (c, d),
                         timestamp_data.sec, timestamp_data.nominal_separation_plane)
    else:
        timestamp_data = map(lambda c,d: (c,'CROSSING' if d == 0 else 'SEPARATION'), timestamp_data.sec, timestamp_data.set_nominal_B1sepPlane)
    timestamp_data = map(lambda c, d: [c, d],
                         timestamp_data[::2], timestamp_data[1::2])

    # Remove last scan if beam was dumped before producing second part of
    # scanpair
    # if len(timestamp_data) % 2 == 1:
    #     message = '\n\t' + 'Uneven number of scans, removing last scan: ' + \
    #         str(timestamp_data[-1])
    #     timestamp_data = timestamp_data[:-1]
    #     print message
    #     logging.warning('\n\t' + dt.datetime.now().strftime(
    #         '%d %b %Y %H:%M:%S\n') + message)
    print timestamp_data
    return timestamp_data


def FormatTimestamps(times):
    """Formats the timestamps into corresponding scan names, timewindows,
        scan pairs, offsets and removes nominal separation plane data
        
        times are in the format that comes out of GetTimestamps
        """
    # Create scan names and pairs
    if not times:
        return False
    rang = range(1, len(times) + 1)
    pairs = []#map(lambda a, b: [a, b], rang[::2], rang[1::2])
    names = []
    crossfirst = True
    for i in xrange(0, len(times)/2):
        if times[2 * i][0][1] == 'CROSSING':
            names.append("X" + str(i + 1))
            names.append("Y" + str(i + 1))
            crossfirst = True
        else:
            names.append("Y" + str(i + 1))
            names.append("X" + str(i + 1))
            crossfirst = False
        if i%2 == 0:
            pairs.append([i+1,i+2] if crossfirst else [i+2,i+1])

    # Get scan data in correct format for auto config
    times = map(lambda a: [a[0][0], a[1][0]], times)

    _scannames = json.dumps(names)
    _timewindows = str(times)
    _scanpairs = str(pairs)
    _offsets = str([0.0 for i in range(len(times))])

    return _scannames, _timewindows, _scanpairs, _offsets, times


def ConfigDriver(times, fillnum, _luminometer, _fit, _ratetable, name, central, first=True, automation_folder='Automation/', _bstar = False, _angle = False, makepdf = True, makelogs = True, autoconfigs_folder = 'na', eff = 0):
    """Makes a folder with configuration files with given timestamps paired for beginnings and endings of scans

        times : should be of the form [ (timestamp, nominal_separation_plane), (timestamp, nominal_separation_plane) ] (like from GetTimestamps)
        name : the name of the analysis folder (fill number and datetimes from the beginning and ending of the scan pair)
        central : the path to the data file or folder. give hd5 file path for emittance scans and folder (currently /brildata/vdmdata17/)
        first : tells whether this configuration should also have scan and beamcurrents files made
        automation_folder : the relative path to folder with your dipfiles, autoconfigs and Analysed_Data folders (default is 'Automation/')
        _bstar and _angle : should be values of those variables if you have them (otherwise default is False)
        makepdf : tells whether to make pdfs with beam beam corrections and fitted functions
        makelogs : tells whether to make logs for the fitting (minuit and otherwise)
        autoconfigs_folder : is the folder where your templates for configurations are"""
    if autoconfigs_folder == 'na':
        autoconfigs_folder = automation_folder
    # time-related data for all configurations
    _scannames, _timewindows, _scanpairs, _offsets, times = FormatTimestamps(
        times)

    # other, more generic data
    _fill = str(fillnum)
    _date = dt.datetime.fromtimestamp(times[0][0]).strftime('%d%b%Y')
    _central = central  # + _fill
    _dip = automation_folder + '/dipfiles/vdm_' + name + '.csv'

    
    # json-compatible true-false`
    true = json.dumps(True)
    false = json.dumps(False)

    _makeScanFile = json.dumps(first)
    _makeRateFile = true
    _makeBeamCurrentFile = json.dumps(first)
    _makeBeamBeamFile = false
    _makeGraphsFile = true
    _runVdmFitter = true
    _makepdf = json.dumps(makepdf)
    _makelogs = json.dumps(makelogs)

    # Start without correction
    _corr = 'noCorr'
    _corrs = json.dumps([_corr])

    path = automation_folder + 'autoconfigs/'
    try:
        os.mkdir(path + name)
    except OSError as e:
        shit = 'happens'
        #print('Folder ' + path + _fill + ' already exists')
        #logging.warning('Folder ' + path + _fill + ' already exists' + '\n'  + str(e))
     
    def Config():
        '''Creates new Driver configuration
            Variables are set outside of function so you only change the ones you
            need different from the last configuration'''
        if _bstar is False:
            with open(autoconfigs_folder + 'vdmDriverII_Autoconfig.json', 'r') as f:
                config = f.read()
            with open(path + name + '/' + _luminometer + _corr + '_' + _fit + '_driver.json', 'w') as f:
                f.write(config.format(fill=_fill, date=_date, scannames=_scannames, timewindows=_timewindows,
                                    analysisdir=automation_folder + 'Analysed_Data/' + name, scanpairs=_scanpairs,
                                    dip=_dip, central=_central, luminometer=_luminometer, fit=_fit, offsets=_offsets,
                                    ratetable=_ratetable, corr=_corr, corrs=_corrs, makeScanFile=_makeScanFile,
                                    makeRateFile=_makeRateFile, makeBeamCurrentFile=_makeBeamCurrentFile, 
                                    makeBeamBeamFile=_makeBeamBeamFile, makeGraphsFile=_makeGraphsFile,
                                    runVdmFitter=_runVdmFitter, makepdf = _makepdf, makelogs = _makelogs))
        else:
            with open(autoconfigs_folder + 'vdmDriverII_Autoconfigv2.json', 'r') as f:
                config = f.read()
            # print config
            # input()
            with open(path + name + '/' + _luminometer + _corr + '_' + _fit + '_driver.json', 'w') as f:
                f.write(config.format(fill=_fill, date=_date, scannames=_scannames, timewindows=_timewindows,
                                    analysisdir=automation_folder + 'Analysed_Data/' + name, scanpairs=_scanpairs,
                                    dip=_dip, central=_central, luminometer=_luminometer, fit=_fit, offsets=_offsets,
                                    ratetable=_ratetable, corr=_corr, corrs=_corrs, makeScanFile=_makeScanFile,
                                    makeRateFile=_makeRateFile, makeBeamCurrentFile=_makeBeamCurrentFile, eff = eff,
                                    makeBeamBeamFile=_makeBeamBeamFile, makeGraphsFile=_makeGraphsFile, runVdmFitter=_runVdmFitter,
                                    bstar = _bstar, angle = _angle,  makepdf = _makepdf, makelogs = _makelogs))
        # Configure calibration constant calculation
        with open(autoconfigs_folder + 'calculateCalibrationConstant_Autoconfig.json', 'r') as f:
            config = f.read()

        with open(path + name + '/' + _luminometer + _corr +
                '_' + _fit + '_calibrationConst.json', 'w') as f:
            f.write(config.format(fill=_fill, date=_date, scanpairs=_scanpairs, analysisdir=automation_folder + 'Analysed_Data/' + name,
                                luminometer=_luminometer, fit=_fit, corrs=_corrs))

        # Configure fit results plotting
        with open(autoconfigs_folder + 'plotFitResults_Autoconfig.json', 'r') as f:
            config = f.read()

        with open(path + name + '/' + _luminometer +
                _corr + '_' + _fit + '_plotFit.json', 'w') as f:
            f.write(config.format(fill=_fill, date=_date,
                                luminometer=_luminometer, fit=_fit, corrs=_corrs,analysisdir=automation_folder + 'Analysed_Data/' + name))

    # Configure a noCorr driver run
    Config()

    # Configure a Beam Beam driver run
    _corr = 'BeamBeam'
    _corrs = json.dumps([_corr])
    _makeScanFile = false
    _makeRateFile = false
    _makeBeamCurrentFile = false
    _makeBeamBeamFile = true
    _makeGraphsFile = true
    _runVdmFitter = true

    Config()

    


def RemapVdMDIPData(olddata):
    '''Remaps a pandas dataframe from the format in which it comes to HD5 files to
        the old vdmdip csv file with added new fields and 0 for total atlas luminosity'''

    data = pd.DataFrame()
    data['fill'] = olddata['fillnum']
    data['run'] = olddata['runnum']
    data['ls'] = olddata['lsnum']
    data['nb'] = olddata['nbnum']
    data['sec'] = olddata['timestampsec']
    data['msec'] = olddata['timestampmsec']
    data['acqflag'] = [int(i == 'ACQUIRING') for i in olddata['stat']]
    data['step'] = olddata['step']
    data['beam'] = olddata['beam']
    data['ip'] = olddata['ip']
    data['scanstatus'] = olddata['stat']
    data['plane'] = olddata['plane']
    data['progress'] = olddata['progress']
    data['nominal_separation'] = olddata['sep']
    
    data['read_nominal_B1sepPlane'] = olddata['r_sepP1']
    data['read_nominal_B1xingPlane'] = olddata['r_xingP1']
    data['read_nominal_B2sepPlane'] = olddata['r_sepP2']
    data['read_nominal_B2xingPlane'] = olddata['r_xingP2']
    data['set_nominal_B1sepPlane'] = olddata['s_sepP1']
    data['set_nominal_B1xingPlane'] = olddata['s_xingP1']
    data['set_nominal_B2sepPlane'] = olddata['s_sepP2']
    data['set_nominal_B2xingPlane'] = olddata['s_xingP2']
    data['atlas_totInst'] = [0 for i in data['fill']]
    
    if 'nominal_sep_plane' in olddata:
        data['nominal_separation_plane'] = olddata['nominal_sep_plane']
        data['bpm_5LDOROS_B1Names'] = olddata['5ldoros_b1names']
        data['bpm_5LDOROS_B1hPos'] = olddata['5ldoros_b1hpos']
        data['bpm_5LDOROS_B1vPos'] = olddata['5ldoros_b1vpos']
        data['bpm_5LDOROS_B1hErr'] = olddata['5ldoros_b1herr']
        data['bpm_5LDOROS_B1vErr'] = olddata['5ldoros_b1verr']
        data['bpm_5RDOROS_B1Names'] = olddata['5rdoros_b1names']
        data['bpm_5RDOROS_B1hPos'] = olddata['5rdoros_b1hpos']
        data['bpm_5RDOROS_B1vPos'] = olddata['5rdoros_b1vpos']
        data['bpm_5RDOROS_B1hErr'] = olddata['5rdoros_b1herr']
        data['bpm_5RDOROS_B1vErr'] = olddata['5rdoros_b1verr']
        data['bpm_5LDOROS_B2Names'] = olddata['5ldoros_b2names']
        data['bpm_5LDOROS_B2hPos'] = olddata['5ldoros_b2hpos']
        data['bpm_5LDOROS_B2vPos'] = olddata['5ldoros_b2vpos']
        data['bpm_5LDOROS_B2hErr'] = olddata['5ldoros_b2herr']
        data['bpm_5LDOROS_B2vErr'] = olddata['5ldoros_b2verr']
        data['bpm_5RDOROS_B2Names'] = olddata['5rdoros_b2names']
        data['bpm_5RDOROS_B2hPos'] = olddata['5rdoros_b2hpos']
        data['bpm_5RDOROS_B2vPos'] = olddata['5rdoros_b2vpos']
        data['bpm_5RDOROS_B2hErr'] = olddata['5rdoros_b2herr']
        data['bpm_5RDOROS_B2vErr'] = olddata['5rdoros_b2verr']
        data['totsize'] = olddata['totsize']
        data['publishnnb'] = olddata['publishnnb']
        data['datasourceid'] = olddata['datasourceid']
        data['algoid'] = olddata['algoid']
        data['channelid'] = olddata['channelid']
        data['payloadtype'] = olddata['payloadtype']
    if 'bstar5' in olddata:
        data['bstar5'] = olddata['bstar5']
        data['xingHmurad'] = olddata['xingHmurad']

    return data


if __name__ == '__main__':
    '''Take all VdM DIP files from 2016 with the correct data format and
        configure analysis for them. You can also choose a specific fill'''
    logging.basicConfig(filename=default_folder + "Automation/Logs/Configurator_" + dt.datetime.now().strftime(
        '%y%m%d%H%M%S') + '.log', level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--fill', help='only used for testing purposes', type=int)
    parser.add_argument('-d', '--dip', help='folder with dip file', default='/brildata/vdm/')
    parser.add_argument('-c', '--central', help='central folder', default='/brildata/17/')

    args = parser.parse_args()
    fillnum = args.fill
    dipdir = args.dip
    central = args.central
    dips = os.listdir(dipdir)
    for dip in dips:
        if dip[-4:] == '.csv' and os.path.getmtime(dipdir + dip) > 1460419200:
            data = pd.read_csv(dipdir + dip)
            if data.shape[0] != 0:
                gb = data.groupby('fill')
                for fill, group in gb:
                    if fillnum and fill == fillnum:
                        times = []

                        def timestamp(i): return dt.datetime.fromtimestamp(
                            group.iloc[i]['sec']).strftime('%y%b%d_%H%M%S')
                        name = str(fill) + '_' + timestamp(0) + \
                            '_' + timestamp(-1)
                        try:
                            times = GetTimestamps(group, fill, name)
                        except:
                            message = '\n\t' + 'Error getting timestamps!\n' + traceback.format_exc()
                            print message
                            logging.error('\n\t' + dt.datetime.now().strftime(
                                '%d %b %Y %H:%M:%S\n') + '\nFill ' + str(fill) + '\nVdM file: ' + dip + message)
                        if times:
                            # for lum,fit,rate in zip(luminometers, fits,
                            # ratetables):
                            for i in range(len(fits)):
                                try:
                                    if os.path.exists(central+str(fill)):
                                        ConfigDriver(
                                            times, fill, luminometers[i], fits[i], ratetables[i], name, central + str(fill), not i)
                                    else:
                                        ConfigDriver(
                                            times, fill, luminometers[i], fits[i], ratetables[i], name, central, not i)
                                except:
                                    message = 'Error making config files\n' + traceback.format_exc()
                                    print message
                                    logging.error('\n\t' + dt.datetime.now().strftime(
                                        '%d %b %Y %H:%M:%S\n') + '\nFill ' + str(fill) + '\nVdM file: ' + dip + message)
