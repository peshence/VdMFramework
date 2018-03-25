import VdManalyze as v

detectors = ['PLT','HFET', 'HFOC']
detector = 'PLT'
folder = '/brildata/vdmoutput/Automation/Analysed_Data/'
bcmfolder = '/brildata/vdmoutput/Automation/Analysed_Data/'

print detector, 'all'
df = v.load_all([detector], main_folder=bcmfolder, forcemodel=True)
df.to_csv(detector + '_const_2017.csv')
print detector, 'leading'
ldf = v.load_all([detector], main_folder=bcmfolder, forcemodel=True, leading = True)
ldf.to_csv(detector + '_const_leading_2017.csv')
print detector, 'train'
tdf = v.load_all([detector], main_folder=bcmfolder, forcemodel=True, train = True)
tdf.to_csv(detector + '_const_train_2017.csv')

# for detector in detectors:
#     print detector, 'all'
#     df = v.load_all([detector], main_folder=folder)
#     df.to_csv(detector + '_const_2017.csv')
#     print detector, 'leading'
#     ldf = v.load_all([detector], main_folder=folder, leading = True)
#     ldf.to_csv(detector + '_const_leading_2017.csv')
#     print detector, 'train'
#     tdf = v.load_all([detector], main_folder=folder, train = True)
#     tdf.to_csv(detector + '_const_train_2017.csv')

