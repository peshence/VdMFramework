import numpy as np
import pandas as pd
import json
import requests
import os
import re

endpoint = 'http://srv-s2d16-22-01.cms:11001/vdm'
testendpoint = 'http://srv-s2d16-22-01.cms:11001/vdmtest'
perchannelendpoint = 'http://srv-s2d16-22-01.cms:11001/vdmch'

def PostOutput(fitresults, calibration, times, fill, run, test, name,
               luminometer, fit, crossing_angle, automation_folder='Automation/', perchannel = False, post=False):
    ''' Posts data to listener service for online monitoring
        fitresults is the fit results table that comes out of vdmFitterII.py and vdmDriverII.py
        calibration is the table that comes out of calculateCalibrationConstant.py
        times is a timestamp collection from scan file or configuration
        test is a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
    '''
    gb = dict(list(fitresults.groupby('Scan')))
    for j in range(len(gb))[::2]:
        local_calibration = calibration.loc[calibration.XscanNumber_YscanNumber == 
                                        str(j + 1) + '_' + str(j + 2)]
        if local_calibration.empty:
            local_calibration = calibration.loc[calibration.XscanNumber_YscanNumber == 
                                        str(j + 2) + '_' + str(j + 1)]
        output = GetOutput(gb[str(j + 1)].append(gb[str(j + 2)]),
                            local_calibration, int(times[j*2][0]),
                               fill, run, luminometer, crossing_angle)
        output.update({'fit': fit})
        if perchannel:
            detector = output['detector']
            detector_channel = re.match('([A-Z1_]*[A-Z]+)_?([0-9]+)', detector)
            detector = detector_channel.group(1)
            channel = detector_channel.group(2)
            output['detector'] = detector
            output.update({'channel':channel})
            if not os.path.exists(automation_folder + 'Analysed_Data/' + name + '/PerChannelJSONS/'):
                os.mkdir(automation_folder + 'Analysed_Data/' + name + '/PerChannelJSONS/')
            with open(automation_folder + 'Analysed_Data/' + name + '/PerChannelJSONS/' + 'output' +
                        str(fill) + luminometer + fit + str(j / 2 + 1) + '.json', 'w') as f:
                json.dump(output,f)
        else:
            with open(automation_folder + 'Analysed_Data/' + name + '/' + 'output' +
                        str(fill) + luminometer + fit + str(j / 2 + 1) + '.json', 'w') as f:
                json.dump(output, f)
        if post:
            if test:
                requests.post(testendpoint, json.dumps(output))
            elif perchannel:
                requests.post(perchannelendpoint, json.dumps(output))
            else:
                requests.post(endpoint, json.dumps(output))


def GetOutput(fitresults, calibration, timestamp, fill, run, detector, crossing_angle):
    '''Gets a json string with xsec, CapSigma, peak, chi2/ndof and SBIL

        fitresults is the fit results table that comes out of vdmFitterII.py and vdmDriverII.py
        calibration is the table that comes out of calculateCalibrationConstant.py
    '''
    output = {'timestamp': timestamp, 'fill': fill, 'run': run,
              'detector': detector, 'crossing_angle': crossing_angle}
    fitresults = fitresults[(fitresults.BCID != 'sum') & (fitresults.BCID != 'wav')]
    calibration = calibration[(calibration.BCID != 'sum') & (calibration.BCID != 'wav')]
    xfitresults = fitresults[(fitresults.Type == 'X')]
    xfitresults.index = xfitresults.BCID
    yfitresults = fitresults[(fitresults.Type == 'Y')]
    yfitresults.index = yfitresults.BCID
    calibration.index = calibration.BCID
    
    convergedfits = (xfitresults.fitStatus == 0) & (yfitresults.fitStatus == 0)
    # calibration = calibration[calibration.BCID.isin(xfitresults.BCID)]

    output.update(GetVariable(xfitresults, convergedfits, 'CapSigma', 'X'))
    output.update(GetVariable(yfitresults, convergedfits, 'CapSigma', 'Y'))

    output.update(GetVariable(xfitresults, convergedfits, 'Mean', 'X'))
    output.update(GetVariable(yfitresults, convergedfits, 'Mean', 'Y'))

    output.update(GetVariable(xfitresults, convergedfits, 'peak', 'X'))
    output.update(GetVariable(yfitresults, convergedfits, 'peak', 'Y'))

    output.update(GetVariable(xfitresults, convergedfits, 'chi2', 'X'))
    output.update(GetVariable(yfitresults, convergedfits, 'chi2', 'Y'))

    output.update(GetVariable(calibration, convergedfits, 'xsec', 'XY'))
    output.update(GetVariable(calibration, convergedfits, 'SBIL', 'XY'))

    GetSlope(output,calibration,convergedfits)

    return output


def GetVariable(data, converged, column, plane):
    '''Gets the data for specific column for specific plane and returns it 
        in dictionary format like values, errors, average, averageerror'''
    outvalues = [0 for i in range(3564)]
    bcids = [int(i) for i in data.BCID]

    if column == 'chi2':
        chi2 = list(data[column])
        ndof = list(data['ndof'])
        chi2ndof = [c / n for c, n in zip(chi2, ndof)]
        for i in range(len(bcids)):
            outvalues[bcids[i] - 1] = chi2ndof[i]
        column = column.lower() + '_' + plane.lower() + '_'
        valAv = column + 'avg'
        column += 'bx'
        return {column: outvalues, valAv: np.mean(chi2ndof)}

    outerrors = [0 for i in range(3564)]

    columnErr = column + 'Err'

    values = list(data[column])
    errors = list(data[columnErr])
    convergedValues = data[converged][column]
    value = np.mean(convergedValues)
    error = np.std(convergedValues)
    for i in range(len(bcids)):
        outvalues[bcids[i] - 1] = values[i]
        outerrors[bcids[i] - 1] = errors[i]
    if column == 'xsec':
        column = 'sigmavis_'
    elif column == 'SBIL':
        column = 'sbil_'
    else:
        column = column.lower() + '_' + plane.lower() + '_'
    valAv = column + 'avg'
    errAv = valAv + '_err'
    column += 'bx'
    columnErr = column + '_err'

    result = {column: outvalues, columnErr: outerrors,
              valAv: value, errAv: error}

    return result

def GetSlope(data,calibration, converged):
    '''
    Gets alinear slope of Sigvis vs SBIL
    data is the complete (except for slopes) json
    '''
    convergedbxs = calibration[converged].BCID

    lsig,lsbil,tsig,tsbil = [],[],[],[]
    for bx in convergedbxs:
        if str(int(bx)-1) in calibration.BCID:
            tsig.append(calibration.xsec[bx])
            tsbil.append(calibration.SBIL[bx]-6)
        else:
            lsig.append(calibration.xsec[bx])
            lsbil.append(calibration.SBIL[bx]-6)
    lm = np.mean(lsig)        
    # lsbil = [i/j*lm for i,j in zip(lsbil,lsig)]
    try:
        (la,lb),lcov = np.polyfit(lsbil,lsig, 1, cov=True)
        lin = la*100/lm
        linerr = np.sqrt(lcov[0,0])*100/lm
        if linerr < lin:
            data['linearity_lead'] = lin
            data['linearity_lead_err'] = linerr
            data['efficiency_lead'] = lb
            data['efficiency_lead_err'] = np.sqrt(lcov[1,1])
    except:
        pass

    if tsig and len(tsig)>0:
        tm = np.mean(tsig)
        # tsbil = [i/j*tm for i,j in zip(tsbil,tsig)]
        try:
            (ta,tb),tcov = np.polyfit(tsbil,tsig, 1, cov=True)
            lin = ta*100/tm
            linerr = np.sqrt(tcov[0,0])*100/tm
            if linerr < lin:
                data['linearity_train'] = lin
                data['linearity_train_err'] = linerr
                data['efficiency_train'] = tb
                data['efficiency_train_err'] = np.sqrt(tcov[1,1])
        except:
            pass
