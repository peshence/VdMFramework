import os
import json
import csv
import datetime as dt
import pickle


anf = '/brildata/vdmoutput/Automation/Analysed_Data/'
tss = []
tse = []
with open("timestamps.csv",'wb') as resultFile:
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerow(['Fill', 'Runs', 'TimestampStart','TimestampEnd'])
    for folder in os.listdir(anf):
        # jsname = next((i for i in os.listdir(anf+folder) if i[-4:]=='json'),0)
        if not str.isdigit(folder[0]):continue
        jsname = next((i for i in os.listdir(anf+folder+'/cond/') if i[-3:]=='pkl' and i[:4] == 'Scan'),0)
        
        if not jsname:continue
        with open(anf+folder+'/cond/'+jsname) as f:
            js = pickle.load(f)
        wr.writerow([js['Fill'],js['Run'],js['ScanTimeWindows'][0][0],js['ScanTimeWindows'][-1][-1]])
        # tss.append()
        # tse.append(js['ScanTimeWindows'][-1][-1])



    # for ts,te in zip(sorted(tss),sorted(tse)):
    #     wr.writerow([ts,te)