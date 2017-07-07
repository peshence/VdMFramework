import numpy as np
import pandas as pd
import json
import requests

endpoint = 'http://srv-s2d16-22-01.cms:11001/vdm'
testendpoint = 'http://srv-s2d16-22-01.cms:11001/vdmtest'

def PostOutput(fitresults, calibration, times, fill, run, test, name, luminometer, fit, crossing_angle, corr = 'noCorr', automation_folder = 'Automation/'):
    ''' Posts data to listener service for online monitoring
        fitresults is the fit results table that comes out of vdmFitterII.py and vdmDriverII.py
        calibration is the table that comes out of calculateCalibrationConstant.py
        times is a timestamp collection of the form that comes out of Configurator.py
        test is a boolean that tells if you want to post to test instance
            (which looks at different fits as different data series) or normal instance
    '''
    gb = dict(list(fitresults.groupby('Scan')))
    for j in range(len(gb))[::2]:
        output = GetOutput(gb[str(j+1)].append(gb[str(j+2)]),
                    calibration.loc[calibration.XscanNumber_YscanNumber == str(j+1) + '_' + str(j+2)],
                    int(times[j][0][0]), fill, run, luminometer, crossing_angle)

        json.dump(output, open(automation_folder + 'Analysed_Data/' + name + '/' + 'output' + str(fill) + luminometer + fit + '.json', 'w'))
        if test:
        #requests.post(endpoint, json.dumps(output))
            output.update({'fit':fit})
            requests.post(testendpoint, json.dumps(output))
        else:
            requests.post(endpoint, json.dumps(output))

def GetOutput(fitresults, calibration, timestamp, fill, run, detector, crossing_angle):
    '''Gets a json string with xsec, CapSigma, peak, chi2/ndof and SBIL
    
        fitresults is the fit results table that comes out of vdmFitterII.py and vdmDriverII.py
        calibration is the table that comes out of calculateCalibrationConstant.py
    '''
    print type(crossing_angle)
    output = {'timestamp':timestamp, 'fill':fill, 'run':run, 'detector':detector, 'crossing_angle':crossing_angle}
    
    output.update(GetVariable(fitresults, 'CapSigma', 'X'))
    output.update(GetVariable(fitresults, 'CapSigma', 'Y'))
    
    output.update(GetVariable(fitresults, 'Mean', 'X'))
    output.update(GetVariable(fitresults, 'Mean', 'Y'))

    output.update(GetVariable(fitresults, 'peak', 'X'))
    output.update(GetVariable(fitresults, 'peak', 'Y'))

    output.update(GetVariable(fitresults, 'chi2', 'X'))
    output.update(GetVariable(fitresults, 'chi2', 'Y'))

    output.update(GetVariable(calibration, 'xsec', 'XY'))
    output.update(GetVariable(calibration, 'SBIL', 'XY'))

    return output


def GetVariable(fitresults, column, plane):
    '''Gets the data for specific column for specific plane and returns it 
        in dictionary format like values, errors, average, averageerror'''
    data = fitresults.loc[(fitresults.BCID != 'sum') & (fitresults.BCID != 'wav') & (fitresults.Type == plane)]
    outvalues = [0 for i in range(3564)]
    bcids = [int(i) for i in data.BCID]

    if column == 'chi2':
        chi2 = list(data[column])
        ndof = list(data['ndof'])
        chi2ndof = [c/n for c,n in zip(chi2,ndof)]
        for i in range(len(bcids)):
            outvalues[bcids[i]-1] = chi2ndof[i]
        column = column.lower() + '_' + plane.lower() + '_'
        valAv = column + 'avg'
        column += 'bx'
        return {column:outvalues, valAv:np.mean(chi2ndof)}
       
    outerrors = [0 for i in range(3564)]

    columnErr = column + 'Err'

    values = list(data[column])
    errors = list(data[columnErr])
    value = np.mean(data[column])
    error = np.mean(data[columnErr])
    for i in range(len(bcids)):
        outvalues[bcids[i]-1] = values[i] 
        outerrors[bcids[i]-1] = errors[i]
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

    result = {column:outvalues, columnErr:outerrors, valAv:value, errAv:error}

    return result
