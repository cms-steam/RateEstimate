#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-
import ROOT
import time
import sys
from math import *
from os import walk
from os import mkdir
from triggersGroupMapPDs import *
from datasetCrossSectionsPhys14 import *

from scipy.stats import binom
def sqrtMod(x):
    if x>0: return sqrt(x)
    else: return 0

def CL(p,n):
    precision1 = 1E-3
    precision2 = 1E-6
    epsilon = 1.*p/n
    epsilon_down = epsilon
    epsilon_up = epsilon
    prob = 0.5
    while prob<0.95:
        epsilon_down/=1+precision1
        prob = binom.cdf(p, n, epsilon_down)
    
    while prob>0.95:
        epsilon_down*=1+precision2
        prob = binom.cdf(p, n, epsilon_down)
    
    while prob>0.05:
        epsilon_up*=1+precision1
        prob = binom.cdf(p-1, n, epsilon_up) 
    
    while prob<0.05:
        epsilon_up/=1+precision2
        prob = binom.cdf(p-1, n, epsilon_up) 
    
    return epsilon_down,epsilon_up

def test_CL(p,n):
    print  1-CL(p,n)[0]-CL(n-p,n)[1]
    print  1-CL(p,n)[1]-CL(n-p,n)[0]

def getTriggersListFromNtuple(chain,triggerListInNtuples):
            for leaf in chain.GetListOfLeaves():
               name = leaf.GetName()
               if (("HLT_" in name) or (evalL1 and ("L1_" in name))) and not ("Prescl" in name):
                triggerListInNtuples.append(name)

def setToZero(totalEventsMatrix,passedEventsMatrix,triggerAndGroupList,rateTriggerTotal,squaredErrorRateTriggerTotal) :
    for dataset in xsectionDatasets:
        totalEventsMatrix[dataset]=0
        for trigger in triggerAndGroupList:
            passedEventsMatrix[(dataset,trigger)]=0
    
    for trigger in triggerAndGroupList:
        rateTriggerTotal[trigger]=0
        squaredErrorRateTriggerTotal[trigger]=0

def writeMatrixEvents(fileName,datasetList,triggerList,totalEventsMatrix,passedEventsMatrix,writeGroup=False):
    f = open(fileName, 'w')
    text = 'Path\t' 
    if writeGroup: text += 'Group\t'
    for dataset in datasetList:
        datasetName = dataset[:-21]
        datasetName = datasetName.replace("-", "")
        datasetName = datasetName.replace("_", "")
        text +=  datasetName + '\t'

    text += '\n'
    text +=  'TotalEvents\t'
    if writeGroup: text += '\t'
    for dataset in datasetList:
        text += str(totalEventsMatrix[dataset]) + '\t'

    for trigger in triggerList:
        text += '\n'
        text +=  trigger+'\t'
        if writeGroup:
            for group in triggersGroupMap[trigger]:
                text += group+','
        
            text=text[:-1] ##remove the last comma
            text += '\t'
        
        for dataset in datasetList:
            text += str(passedEventsMatrix[(dataset,trigger)]) + '\t'

    f.write(text)
    f.close()

def writeMatrixRates(fileName,datasetList,rateTriggerDataset,rateTriggerTotal,triggerList,writeGroup=False):
    f = open(fileName, 'w')
    text = 'Path\t'
    if writeGroup: text += 'Group\t'
    text += 'Total\t\t\t'
    for dataset in datasetList:
        datasetName = dataset[:-21]
        datasetName = datasetName.replace("-", "")
        datasetName = datasetName.replace("_", "")
        text +=  datasetName + '\t\t\t'

    for trigger in triggerList:
        text += '\n'
        text +=  trigger+'\t'
        if writeGroup:
            for group in triggersGroupMap[trigger]:
                text += group+','
        
            text=text[:-1] ##remove the last comma
            text += '\t'
        
        text += str(rateTriggerTotal[trigger])+'\t±\t'+str(sqrtMod(squaredErrorRateTriggerTotal[trigger]))+'\t'
        for dataset in datasetList:
            text += str(rateTriggerDataset[(dataset,trigger)]) + '\t±\t' + str(sqrtMod(squaredErrorRateTriggerDataset[(dataset,trigger)])) + '\t'

    f.write(text)
    f.close()

def CompareGRunVsGoogleDoc(datasetList,triggerList,folder):
    dirpath=''
    filenames=[]
    for dataset in datasetList:
        for (dirpath, dirnames, filenames) in walk(folder+'/'+dataset):
            if len(filenames)>0 and 'root' in filenames[0]: break
    
    if len(filenames) is 0:
        raise ValueError('No file found in '+folder)
    
    _file0 = ROOT.TFile.Open(dirpath+'/'+filenames[0])
    chain = ROOT.gDirectory.Get("HltTree")

    triggerListInNtuples = []
    getTriggersListFromNtuple(chain,triggerListInNtuples)
    intersection = set(triggerListInNtuples).intersection(triggerList)
    diffTriggersGRun = triggerListInNtuples [:]
    diffTriggersGoogle = triggerList [:]

    for i in intersection:
        diffTriggersGRun.remove(i)
        diffTriggersGoogle.remove(i)

    diffTriggersGRun.sort()
    diffTriggersGoogle.sort()
    print 
    print '#'*30,"Triggers only in GRun:",'#'*30
    for t in diffTriggersGRun:
        print t
    print 
    print '#'*30,"Triggers only in Google doc:",'#'*30
    for t in diffTriggersGoogle:
        print t

    for trigger in triggerList:
        if trigger in diffTriggersGoogle: triggerList.remove(trigger)
    
    triggerList = intersection
    return triggerList

def getEvents(filepath):
        passedEventsMatrix_={}
        tree = None
        try:
            _file0 = ROOT.TFile.Open(filepath)
            tree=ROOT.gDirectory.Get("HltTree")
        except:
            pass
        
        isEMEnriched = False
        isMuEnriched = False
        isAntiEM = False
        isAntiMu = False
        
        for datasetEM in datasetEMEnrichedList:
            if datasetEM in filepath.split("/"): isEMEnriched = True
        
        for datasetMu in datasetMuEnrichedList:
            if datasetMu in filepath.split("/"): isMuEnriched = True
        
        for datasetAntiMu in datasetAntiMuList:
            if datasetAntiMu in filepath.split("/"): isAntiMu = True
        
        for datasetAntiEM in datasetAntiEMList:
            if datasetAntiEM in filepath.split("/"): isAntiEM = True
        
        filterString = '1'
        
        ## skip file if you have to
        if (not useMuEnriched) and isMuEnriched: tree = None
        if (not useEMEnriched) and isEMEnriched: tree = None
        
        ## apply PU filter
        if pileupFilter and ('QCD'in filepath):
            if pileupFilterGen: filterString += '&&HLT_RemovePileUpDominatedEventsGen_v1'
            else: filterString += '&&HLT_RemovePileUpDominatedEvents_v1'
        
        ## if useEMEnriched, apply AntiEM cut 
        if useEMEnriched and isAntiEM: filterString += '&& !'+EM_cut
        
        ## if useMuEnriched, apply AntiMu cut
        if useMuEnriched and isAntiMu: filterString += '&& !'+Mu_cut
        
        denominatorString = '1'
        ## if useEMEnriched and is EMEnriched, apply EM cut 
        if useEMEnriched and isEMEnriched:
            filterString += '&& '+EM_cut
            denominatorString += '&& '+EM_cut
        
        ## if useMuEnriched and is MuEnriched, apply Mu cut 
        if useMuEnriched and isMuEnriched:
            filterString += '&& '+Mu_cut
            denominatorString += '&& '+Mu_cut
        
        
        if "hltbits_1.root" in filepath:
            print "File: ",filepath
            print "using numerator filter:",filterString
            print "using denominator filter:",denominatorString
            
        if (tree!=None): ##if tree was defined
            totalEventsMatrix_ = tree.Draw("",denominatorString)
            for triggerName in triggerList:
                passedEventsMatrix_[triggerName] = tree.Draw("",'('+triggerName+')&&('+filterString+')')
            
            for groupName in groupList:
                passedEventsMatrix_[groupName] = tree.Draw("",'('+groupToString[groupName]+')&&('+filterString+')')

            for twoGroupsName in twoGroupsList:
                passedEventsMatrix_[twoGroupsName] = tree.Draw("",'('+twoGroupsToString[twoGroupsName]+')&&('+filterString+')')
            
            _file0.Close()
        else:  ##if tree was undefined/empty
            totalEventsMatrix_ = 0
            for triggerName in triggerList:
                passedEventsMatrix_[triggerName] = 0
            
            for groupName in groupList:
                passedEventsMatrix_[groupName] = 0

            for twoGroupsName in twoGroupsList:
                passedEventsMatrix_[twoGroupsName] = 0
        
        return passedEventsMatrix_,totalEventsMatrix_

def fillMatrixAndRates(dataset,totalEventsMatrix,passedEventsMatrix,rateTriggerDataset,squaredErrorRateTriggerDataset):
    start = time.time()
    dirpath=''
    filenames=[]
    for (dirpath, dirnames, filenames) in walk(folder+'/'+dataset):
       if len(filenames)>0 and 'root' in filenames[0]: break

    if dirpath=='':
        print
        print '#'*90
        print '#'*10,"dataset=",dataset," not found!", '#'*10
        print '#'*90
#        return
    
    xsection = xsectionDatasets[dataset] #pb
    rateDataset [dataset] = lumi*xsection*1E-24/1E12 # [ 1.4E34 *1E-24/1E12 = 1.4E-2 ]
    if log>1:
        print
        print "Loading folder: ",dirpath
        print "nfiles=",len(filenames)
        print "TotRateBin=",rateDataset [dataset]
    
    filepaths = []
    for filename in filenames:
        filepaths.append(dirpath+'/'+filename)

    if multiprocess>1:
        p = Pool(multiprocess)
        output = p.map(getEvents, filepaths)

    for filepath in filepaths:
        if multiprocess>1: (passedEventsMatrix_,totalEventsMatrix_) = output[filepaths.index(filepath)]
        else: (passedEventsMatrix_,totalEventsMatrix_) = getEvents(filepath)

        totalEventsMatrix[dataset] += totalEventsMatrix_
        for trigger in triggerAndGroupList:
            passedEventsMatrix[(dataset,trigger)] += passedEventsMatrix_[trigger]
        
    if totalEventsMatrix[dataset]==0:   totalEventsMatrix[dataset]=1 ## do not crash if a dataset is missing!
    for trigger in triggerAndGroupList:
        rateTriggerDataset [(dataset,trigger)] = rateDataset[dataset]/totalEventsMatrix[dataset]*passedEventsMatrix[(dataset,trigger)]
        squaredErrorRateTriggerDataset [(dataset,trigger)] = rateDataset[dataset]*rateDataset[dataset]*passedEventsMatrix[(dataset,trigger)]/totalEventsMatrix[dataset]/totalEventsMatrix[dataset] # (rateDataset*sqrt(1.*passedEvents/nevents/nevents)) **2
    end = time.time()
    print "Time=",round((end - start),2)," Events=",totalEventsMatrix[dataset]," TimePer10kEvent=", round((end - start)*10000/totalEventsMatrix[dataset],2)

################################################################################################################
## start the script
startGlobal = time.time() ## timinig stuff

## use options:
#folder = 'HLTRates_V6'
#folder = 'HLTRates_V5'
#folder = '/gpfs/ddn/srm/cms/store/user/sdonato/HLTRates_V7/'
#folder = '/gpfs/ddn/srm/cms/store/user/sdonato/HLTRates_74X_50ns_V7/'
folder = '/scratch/sdonato/STEAM/Rate_74X/PU30BX50/HLTRates_74X_50ns_Phys14_newBtag_V9/'
lumi =  5E33 # s-1cm-2
log = 2 # use log=2
multiprocess = 32           # number of processes
pileupFilter = True         # use pile-up filter?
pileupFilterGen = False     # use pile-up filter gen or L1?
useEMEnriched = False       # use plain QCD mu-enriched samples (Pt30to170)?
useMuEnriched = False       # use plain QCD EM-enriched samples (Pt30to170)?
evalHLTpaths = False        # evaluate HLT triggers rates?
evalHLTgroups = False       # evaluate HLT triggers groups rates  ?
evalHLTtwogroups = False    # evaluate the correlation on the HLT trigger groups rates?
evalL1 = False              # evaluate L1 triggers rates?
label = "rates_Hermine_V10"

EM_cut = "(!HLT_BCToEFilter_v1 && HLT_EmFilter_v1)"
#Mu_cut = "(HLT_MuFilter_v1)"
Mu_cut = "MCmu3"

#if useEMEnriched:    datasetList+=datasetEMEnrichedList
#if useMuEnriched:    datasetList+=datasetMuEnrichedList

datasetList=datasetQCD15+datasetList
datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList

print
print "Folder: ", folder
print "Luminosity: ", lumi
print "Use QCDEMEnriched? ", useEMEnriched
print "Use QCDMuEnriched? ", useMuEnriched
print "Evaluate L1 triggers? ", evalL1
print "Pile-up filter: ", pileupFilter
print "Pile-up filterGen: ", pileupFilterGen
print

# load library for multiprocessing
if multiprocess>1: 
    from multiprocessing import Pool
    print "Using up to ", multiprocess ," processes."

## check trigger list in triggersGroupMap -> Google doc, with the ntuple -> GRun
triggerList = CompareGRunVsGoogleDoc(datasetList,triggerList,folder)

## initialization
passedEventsMatrix = {} #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
totalEventsMatrix = {} #totalEventsMatrix[(dataset,trigger)] = total events of a dataset
rateDataset = {} #rateDataset[dataset] = rate of a dataset (xsect*lumi)
rateTriggerDataset = {}  #rateTriggerDataset[(dataset,trigger)] = rate of a trigger in a dataset
squaredErrorRateTriggerDataset = {}  #squaredErrorRateTriggerDataset[(dataset,trigger)] = squared error on the rate
rateTriggerTotal = {}  #rateTriggerTotal[(dataset,trigger)] = total rate of a trigger
squaredErrorRateTriggerTotal = {} #squaredErrorRateTriggerTotal[trigger] = squared error on the rate
setToZero(totalEventsMatrix,passedEventsMatrix,triggerAndGroupList,rateTriggerTotal,squaredErrorRateTriggerTotal)  #set dictionaries to zero

## loop on dataset and fill matrix with event counts, rates, and squared errors
for dataset in datasetList:
    fillMatrixAndRates(dataset,totalEventsMatrix,passedEventsMatrix,rateTriggerDataset,squaredErrorRateTriggerDataset)

## evaluate the total rate (and error) for triggers and groups
for dataset in datasetList:
    for trigger in triggerAndGroupList:
        if
            (evalL1 and (trigger in L1List)) or
            (evalHLT and (trigger in HLTList)) or
            (evalHLTgroups and (trigger in groupList)) or
            (evalHLTtwogroups and (trigger in twoGroupsList)) or
        :
            rateTriggerTotal[trigger] += rateTriggerDataset[(dataset,trigger)]
            squaredErrorRateTriggerTotal[trigger] += squaredErrorRateTriggerDataset[(dataset,trigger)]


filename = 'Results/'
filename += label
if pileupFilter:
    if pileupFilterGen:filename += '_PUfilterGen'
    else:filename += '_PUfilter'

if useEMEnriched: filename += '_EMEn'
if useMuEnriched: filename += '_MuEn'

try:
    mkdir("Results")
except:
    pass

## write files with events count
if evalL1: writeMatrixEvents(filename+'_L1.matrixEvents.csv',datasetList,L1List,totalEventsMatrix,passedEventsMatrix,True)
if evalHLTpaths: writeMatrixEvents(filename+'_matrixEvents.csv',datasetList,HLTList,totalEventsMatrix,passedEventsMatrix,True)
if evalHLTgroups: writeMatrixEvents(filename+'_matrixEvents.groups.csv',datasetList,groupList,totalEventsMatrix,passedEventsMatrix)
if evalHLTtwogroups: writeMatrixEvents(filename+'_matrixEvents.twogroups.csv',datasetList,twoGroupsList,totalEventsMatrix,passedEventsMatrix)

## write files with  trigger rates
if evalL1:writeMatrixRates(filename+'_L1_matrixRates.csv',datasetList,rateTriggerDataset,rateTriggerTotal,L1List,True)
if evalHLTpaths: writeMatrixRates(filename+'_matrixRates.csv',datasetList,rateTriggerDataset,rateTriggerTotal,HLTList,True)
if evalHLTgroups: writeMatrixRates(filename+'_matrixRates.groups.csv',datasetList,rateTriggerDataset,rateTriggerTotal,groupList)
if evalHLTtwogroups: writeMatrixRates(filename+'_matrixRates.twogroups.csv',datasetList,rateTriggerDataset,rateTriggerTotal,twoGroupsList)


## print timing
endGlobal = time.time()
totalEvents = 0
for dataset in datasetList: totalEvents+=totalEventsMatrix[dataset]
print
print "Total Time=",round((endGlobal - startGlobal),2)," Events=",totalEvents," TimePer10kEvent=", round((endGlobal - startGlobal)*10000/totalEvents,2)



