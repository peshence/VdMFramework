import pandas as pd, pylab as py, sys, os, tempfile, subprocess

print 'VdManalyze v1.0'

def load_integrated_lumi(fill_start = 1, fill_end = 9999):
    tmpf = tempfile.NamedTemporaryFile()

    subprocess.call(['brilcalc','lumi','--begin',str(fill_start),'--end',str(fill_end),'-o',tmpf.name,'-u','/nb'])

    data = pd.read_csv(tmpf.name,skiprows=1)
    data = data[:-3]

    lumi = pd.DataFrame()
    lumi['fill'] = data.apply(lambda row: int(row['#run:fill'].split(":")[1]),axis=1)
    lumi['delivered'] = data.apply(lambda row: float(row['delivered(/nb)']),axis=1)
    lumi = lumi.groupby(by='fill').sum()
    lumi['integrated'] = lumi.cumsum()

    return lumi



def load_all(luminometers,fill_start = 0, fill_end = 99999, BX=[],peakmax=False, PLTcapsigma=False,main_folder = '/brildata/vdmoutput/Automation/Analysed_Data/',forcemodel=False, leading = False, train = False):
    #if return_object not in ['dataframe','dict']: raise ValueError("return_object can only be 'dataframe' or 'dict'")
    scans = check_fills(main_folder=main_folder,forcemodel=forcemodel)
    scans = scans[(scans.fill>=fill_start) & (scans.fill<=fill_end)]

    all_results = pd.DataFrame()
    for timestamp,scan in scans.iterrows():
        print "Processing fill",scan.fill
        lm = [l for l in luminometers if l in  scan.luminometers]
        for subscan in range(scan.subscans):
            if len(scan.model) >=1:
                model = scan.model[0]
            else:
                model = 'SG' # If standard model cant be found, default back to SG
            if train or leading:
                filename = main_folder + scan.folder+'/BCM1FPCVD/results/BeamBeam/LumiCalibration_BCM1FPCVD_'+model+'_'+str(scan.fill)+'.csv'
                try:
                    if not os.path.exists(filename):
                        filename = filename.replace('BCM1FPCVD','PLT')
                    if not os.path.exists(filename):
                        filename = filename.replace('PLT','HFET').replace('SG','SGConst').replace('DG','DGConst')
                except:
                    filename = filename.replace('BCM1FPCVD','HFET').replace('PLT','HFET').replace('SG','SGConst').replace('DG','DGConst')
                availableBXs = [ int(i) for i in pd.DataFrame.from_csv(filename).BCID if str.isdigit(str(i)[0]) ]
                if availableBXs and len(availableBXs) != 0:
                    if leading:
                        BX = [i for i in availableBXs if i-1 not in availableBXs]
                    elif train:
                        BX = [i for i in availableBXs if i-1 in availableBXs]

            all_results[timestamp] =  makeAVGsigvis(scan.fill,scan_number=-1,scan_folder_direct = scan.folder,subscan = subscan,
                channels = lm,model = model,PLTcapsigma = (scan.hasPLT and PLTcapsigma),verbose=False,create_plot=False,BX=BX,
                peakmax=peakmax,main_folder=main_folder,forcemodel=forcemodel)
    return all_results.transpose()


def check_fills(main_folder = '/brildata/vdmoutput/Automation/Analysed_Data/', forcemodel=False):
    all_folders = os.listdir(main_folder)
    scan_folders = [scan for scan in all_folders if ((scan != 'FillBackups') and (scan != 'Fill6016_Jul282017'))] # idea: split string with '_' and check length as qualifier
    fills = [int(sf.split('_')[0]) for sf in scan_folders]
    start_time = [pd.to_datetime(sf.split('_')[1]+sf.split('_')[2], format = '%d%b%y%H%M%S') for sf in scan_folders]

    hasPLT = [False]*len(scan_folders)

    model = []
    subscan = []

    luminometers = []

    for i,scan,fill in zip(range(len(scan_folders)),scan_folders,fills):
        filesinscan = os.listdir(main_folder+scan)

        exclude_list = ['corr', 'cond', 'LuminometerData']
        lftmp =[f for f in filesinscan if (os.path.isdir(main_folder+scan+'/'+f) and f not in exclude_list)]
        lftmp2 = []
        for lf in lftmp:
            if lf[0:3] == 'PLT':
                model2 = ''
            else:
                model2 = 'Const'
            if forcemodel:
                model2 = ''

            f1 = main_folder+scan+'/'+lf+'/results/BeamBeam/LumiCalibration_'+lf+'_SG'+model2+'_'+str(fill)+'.csv'
            f2 = main_folder+scan+'/'+lf+'/results/BeamBeam/LumiCalibration_'+lf+'_DG'+model2+'_'+str(fill)+'.csv'
            if os.path.isfile(f1) or os.path.isfile(f2):
                lftmp2.append(lf)

        luminometers.append(lftmp2)



        files_to_check =[main_folder+scan+'/PLT/results/BeamBeam/LumiCalibration_PLT_SG_'+str(fill)+'.csv',
                        main_folder+scan+'/PLT/results/BeamBeam/LumiCalibration_PLT_DG_'+str(fill)+'.csv',
                        main_folder+scan+'/HFET/results/BeamBeam/LumiCalibration_HFET_SGConst_'+str(fill)+'.csv',
                        main_folder+scan+'/HFET/results/BeamBeam/LumiCalibration_HFET_DGConst_'+str(fill)+'.csv',
                        main_folder+scan+'/BCM1FPCVD/results/BeamBeam/LumiCalibration_BCM1FPCVD_SG_'+str(fill)+'.csv',
                        main_folder+scan+'/BCM1FPCVD/results/BeamBeam/LumiCalibration_BCM1FPCVD_DG_'+str(fill)+'.csv',
                        ]
        modeltmp = []
        if os.path.isfile(files_to_check[0]):
            Lumidata = pd.read_csv(files_to_check[0])
            modeltmp.append('SG')
            hasPLT[i] = True
            if os.path.isfile(files_to_check[1]): modeltmp.append('DG')
        elif os.path.isfile(files_to_check[1]):
            Lumidata = pd.read_csv(files_to_check[1])
            modeltmp.append('DG')
            hasPLT[i] = True
        elif os.path.isfile(files_to_check[2]):
            Lumidata = pd.read_csv(files_to_check[2])
            modeltmp.append('SG')
            if os.path.isfile(files_to_check[3]): modeltmp.append('DG')
        elif os.path.isfile(files_to_check[3]):
            Lumidata = pd.read_csv(files_to_check[3])
            modeltmp.append('DG')
        elif os.path.isfile(files_to_check[4]):
            Lumidata = pd.read_csv(files_to_check[4])
            modeltmp.append('SG')
            if os.path.isfile(files_to_check[5]): modeltmp.append('DG')
        elif os.path.isfile(files_to_check[5]):
            Lumidata = pd.read_csv(files_to_check[5])
            modeltmp.append('DG')
        else:
            subscan.append(0)		
        try:
            subscan.append(len(Lumidata.groupby('XscanNumber_YscanNumber')))
        except:
            pass
        model.append(modeltmp)



#	print len(model)
#	print len(subscan)
#	print len(hasPLT)

    fills_overview = pd.DataFrame(zip(scan_folders,fills,model,subscan,hasPLT,luminometers), index = start_time, columns = ['folder','fill','model','subscans','hasPLT','luminometers'])
    return fills_overview.sort_index()


def makeAVGsigvis(fill,scan_number=0,subscan = 0,channels = ['PLT'],
                    model = 'SG',scan_folder_direct ='',main_folder = '/brildata/vdmoutput/Automation/Analysed_Data/',
                    verbose=True,PLTcapsigma = True,create_plot=True,BX=[],peakmax=False,albedo_corr = None,forcemodel=False):
    output = pd.Series()

    fill = str(fill)

    allscans = os.listdir(main_folder)
    fillscans = [scan for scan in allscans if fill in scan]

    if (scan_number == -1) and (scan_folder_direct !=''):
        scan_folder = scan_folder_direct
        scan_number = py.where(scan_folder == py.array(fillscans))[0][0]
        if verbose: print 'VdM result of scan folder '+scan_folder
    else:
        scan_folder = fillscans[scan_number]
        if verbose:
            print 'VdM result of fill '+ fill+' scan number '+str(scan_number)
            print 'Date: '+ scan_folder.split('_')[1]

    # scan number
    subscanX = subscan*2+1
    subscanY = subscan*2+2


    #initila output
    output['Date'] = scan_folder.split('_')[1]
    output['Fill'] = int(fill)
    output['scan_number'] = str(scan_number)
    output['scan_number_int'] = int(scan_number)
    
    output['subscan'] = subscan
    output['fit_model'] = model


    # get PLT reference Capsigma and SBIL
    if PLTcapsigma:
        filePLT = main_folder+scan_folder+'/'+'PLT/results/BeamBeam/'+model+'_FitResults.csv'
        dataPLT = pd.read_csv(filePLT)
        dataPLT = dataPLT[(dataPLT.BCID!='sum') & (dataPLT.BCID!='wav')]
        #dataPLT = dataPLT[(dataPLT.Scan == subscanX)|(dataPLT.Scan == subscanY)]
        dataPLT['BCID'] = dataPLT['BCID'].astype(int)
        dataPLT = dataPLT.set_index('BCID')
        if len(BX)>=1:
            dataPLT = dataPLT.loc[BX,:]
        capSigList = []
        for key,df in dataPLT.loc[:,['CapSigma','Type']].groupby('Type'):
            capSigList.append(df.rename(index=int,columns={'CapSigma':'CapSigma'+key}))
        capSigPLT = pd.concat(capSigList,axis=1)

        PLTLumidata = pd.read_csv(main_folder+scan_folder+'/PLT/results/BeamBeam/LumiCalibration_PLT_'+model+'_'+fill+'.csv')
        PLTLumidata = PLTLumidata[(PLTLumidata.BCID!='sum') & (PLTLumidata.BCID!='wav')]
        PLTLumidata = PLTLumidata[PLTLumidata.XscanNumber_YscanNumber == str(subscanX)+'_'+str(subscanY)]
        PLTLumidata['BCID'] = PLTLumidata['BCID'].astype(int)
        PLTLumidata = PLTLumidata.set_index('BCID')
                
        if len(BX)>=1:
            PLTLumidata = PLTLumidata.loc[BX,:]



        if verbose: print 'SBIL: ', PLTLumidata.SBIL.mean(), ' +/- ', PLTLumidata.SBIL.std()
        output['PLT_SBIL']= PLTLumidata.SBIL.mean()



    for i,channel in enumerate(channels):
        if channel[0:3] == 'PLT':
            model2 = ''
        else:
            model2 = 'Const'

        if forcemodel:
            model2 = ''
        
        isPLT = False
        if channel == 'PLT': isPLT = True
        
        Lumidata = pd.read_csv(main_folder+scan_folder+'/'+channel+'/results/BeamBeam/LumiCalibration_'+channel+'_'+model+model2+'_'+fill+'.csv')
        try:
            Lumidata = Lumidata[(Lumidata.BCID!='sum') & (Lumidata.BCID!='wav')]
        except:
            pass
        #Lumidata = Lumidata[Lumidata.XscanNumber_YscanNumber == str(subscanX)+'_'+str(subscanY)]
        #BCM1FLumidata = BCM1FLumidata[BCM1FLumidata.XscanNumber_YscanNumber == '3_4']
        Lumidata['BCID'] = Lumidata['BCID'].astype(int)
        Lumidata = Lumidata.set_index('BCID')

        # number of colliding bunches (output only once, overwrite in loop, does not matter)
        output['nbx'] = len(Lumidata)
        # number of used bxs
        output['usedbx'] = len(Lumidata)

        # make this selection after the counting of bunches.
        if len(BX)>=1:
            Lumidata = Lumidata.loc[BX,:]
            output['usedbx'] = len(BX)


        # Average SBIL
        output[channel+'_SBIL']= Lumidata.SBIL.mean()
        if verbose: print 'SBIL: ', Lumidata.SBIL.mean(), ' +/- ', Lumidata.SBIL.std()

        # Slope of xsec vs SBIL
        a,b,cov = py.nan, py.nan, py.array([[py.nan, py.nan], [py.nan, py.nan]])
        xsecm = py.mean(Lumidata.xsec)
        if output['usedbx'] > 2:
            # print py.polyfit(Lumidata.SBIL,Lumidata.xsec, 1, w=[1/i for i in Lumidata.xsecErr], cov=True)
            try:
                constSBIL = (Lumidata.SBIL*Lumidata.xsec)/Lumidata.xsec.mean()
                (a,b),cov = py.polyfit(constSBIL,Lumidata.xsec, 1, cov=True)
                # (a,b),cov = py.polyfit(constSBIL,Lumidata.xsec, 1, w=[1/i for i in Lumidata.xsecErr], cov=True)
            except Exception as e:
                print( 'fitting failed:\n', e)
        output[channel + '_Slope[%]'] = a/xsecm*100
        output[channel + '_SlopeAbsErr[%]'] = cov[0,0]/xsecm*100
        output[channel + '_Intercept[ub]'] = b
        output[channel + '_InterceptErr[ub]'] = cov[1,1]
            

        fileSig = main_folder+scan_folder+'/'+channel+'/results/BeamBeam/'+model+model2+'_FitResults.csv'
        dataSig = pd.read_csv(fileSig)
        try:
            dataSig = dataSig[(dataSig.BCID!='sum') & (dataSig.BCID!='wav')]
        except:
            pass
        dataSig = dataSig[(dataSig.Scan == subscanX)|(dataSig.Scan == subscanY)]
        dataSig['BCID'] = dataSig['BCID'].astype(int)
        dataSig = dataSig.set_index('BCID')
        if len(BX)>=1:
            dataSig = dataSig.loc[BX,:]

        capSigList = []
        for key,df in dataSig.loc[:,['CapSigma','Type','peak','Mean','chi2']].groupby('Type'):
            capSigList.append(df.rename(index=int,columns={'CapSigma':'CapSigma'+key,'peak':'peak'+key,'Mean':'mean'+key,'chi2':'chi2'+key}))
        capSig = pd.concat(capSigList,axis=1)

        output[channel+'_meanX'] = capSig.meanX.mean()
        output[channel+'_meanY'] = capSig.meanY.mean()
        output[channel+'_CapSigmaX'] = capSig.CapSigmaX.mean()
        output[channel+'_CapSigmaY'] = capSig.CapSigmaY.mean()
        output[channel+'_peakX'] = capSig.peakX.mean()
        output[channel+'_peakY'] = capSig.peakY.mean()
        output[channel+'_chi2X'] = capSig.chi2X.mean()
        output[channel+'_chi2Y'] = capSig.chi2Y.mean()

        if peakmax:
            peak = capSig.loc[:,['peakX','peakY']].max(axis=1)
            Xsec_calculated = py.pi * 2*peak * capSig.CapSigmaX * capSig.CapSigmaY  * 1e6
            if PLTcapsigma: Xsec_calculated_PLT = py.pi *2*peak * capSigPLT.CapSigmaX * capSigPLT.CapSigmaY  * 1e6
        else:
            Xsec_calculated = py.pi * (capSig.peakX + capSig.peakY) * capSig.CapSigmaX * capSig.CapSigmaY  * 1e6
            if PLTcapsigma: Xsec_calculated_PLT = py.pi * (capSig.peakX + capSig.peakY) * capSigPLT.CapSigmaX * capSigPLT.CapSigmaY  * 1e6


        if albedo_corr is not None:
            Xsec_calculated_uncor = Xsec_calculated
            Xsec_calculated = Xsec_calculated * (1- albedo_corr)
            Xsec_calculated.dropna(inplace=True)
            if PLTcapsigma:
                Xsec_calculated_PLT_uncor = Xsec_calculated_PLT
                Xsec_calculated_PLT = Xsec_calculated_PLT  * (1- albedo_corr)
                Xsec_calculated_PLT.dropna(inplace=True)

        if verbose:
            print channel
            print 'sigmavis (own CapSigma): ',Xsec_calculated.mean(), ' +/- ',Xsec_calculated.std()
            if PLTcapsigma: print 'sigmavis (PLT CapSigma): ',Xsec_calculated_PLT.mean(), ' +/- ',Xsec_calculated_PLT.std()


        output[channel+'_sigmavis'] = Xsec_calculated.mean()
        output[channel+'_sigmavis_err'] = Xsec_calculated.std()
        output[channel+'_sigmatest'] = Lumidata.xsec.mean()
        output[channel+'_sigmatest_err'] = py.sqrt((Lumidata.xsecErr**2).sum())/len(Lumidata)
        
        if PLTcapsigma and not isPLT:
            output[channel+'_sigmavis_PLTcapsig'] = Xsec_calculated_PLT.mean()
            output[channel+'_sigmavis_PLTcapsig_err'] = Xsec_calculated_PLT.std()
        
        if create_plot:
            py.figure(i,facecolor='white')
            py.errorbar(Xsec_calculated.index,Xsec_calculated,Lumidata.xsecErr,label = 'own capsig',fmt='o')#,where='post')
            if albedo_corr is not None:py.errorbar(Xsec_calculated.index,Xsec_calculated_uncor,Lumidata.xsecErr,label = 'original',fmt='o')#,where='post')
            if PLTcapsigma: py.plot(Xsec_calculated_PLT.index,Xsec_calculated_PLT,'o',label = 'PLT capsig')#,where='post')
            if PLTcapsigma and (albedo_corr is not None): py.plot(Xsec_calculated_PLT.index,Xsec_calculated_PLT_uncor,'o',label = 'PLT capsig orig')#,where='post')
            py.legend()
            py.grid()
            py.ylabel('sigma vis [ub]')
            py.xlabel('BCID')
            py.title('VdM scan result for '+channel+', fill '+fill+', scan '+str(scan_number))

            py.figure(99,facecolor='white')
            if False: py.plot(PLTLumidata.index,PLTLumidata.SBIL,'b.', label = 'PLT')#,where='post')
            py.plot(Lumidata.index,Lumidata.SBIL,'.', label = channel)#,where='post')
            py.grid()
            py.legend()
            py.ylabel('SBIL')
            py.xlabel('BCID')
            py.title('VdM scan result for '+channel+', fill '+fill)

    return output


if __name__ == "__main__":
    print "Please load VdM analyze as module."
    print "Type 'help' to show available functions (quit help qith q)"
    h = raw_input()
    if h == 'help': help(__name__)
