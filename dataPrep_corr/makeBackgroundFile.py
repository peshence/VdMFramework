import numpy as np
import tables

def GetBackground(filename, rateTable):
    '''
        Gets a single beam induced background plus noise estimation from filled non-colliding 
        bunches and a noise value from the abort gap getting to calculate a background value as
        2*(BIM + noise) - noise
        and estimates an error on it which is a standard deviation (should maybe be an error on
        the mean but that makes it perhaps misleadingly small)
    '''
    if rateTable=='hfetlumi':
        return (0,0)
    removestrays = lambda a: np.array([False if i < 6e9 else True for i in a])
    with tables.open_file(filename) as hd5:
        for r in hd5.root.beam:
            bunchlist1 = removestrays(r['bxintensity1'])
            bunchlist2 = removestrays(r['bxintensity2'])

            fillednoncolliding = (bunchlist1 | bunchlist2) & ~(bunchlist1 & bunchlist2)
            break

        for table in hd5.root:
                if table.name == rateTable:
                    beamtable = table
                    break
        
        backgrounds = []
        noises = []
        for r in beamtable:
            backgrounds.append(np.mean(r['bxraw'][fillednoncolliding]))
            noises.append(np.mean(r['bxraw'][-120:]))
        background = np.mean(backgrounds)
        noise = np.mean(noises)
        return ((2*background - noise), np.sqrt(4*np.std(backgrounds)**2 + np.std(noises)**2))

def MakeBackgroundFile(ConfigInfo):
    '''
        Returns a dictionary with a background ('background') and an error ('backgroundError') estimation on it for the whole hd5 
        file in question. Since the std on the background affects the results very little 
        (even when in the 10s of %) this should be good enough

        DOES NOT WORK IF YOU'RE WORKING WITH MORE THAN ONE DATA FILE 
        (central folder instead of single hd5 file)

        ConfigInfo: should be a dictionary with a Filename, RateTable and AnalysisDir properties
    '''
    filename = ConfigInfo['Filename']
    rateTable = ConfigInfo['RateTable']

    bg, bgerr = GetBackground(filename, rateTable)
    
    d={}
    d['background'] = bg
    d['backgroundError'] = bgerr

    return d