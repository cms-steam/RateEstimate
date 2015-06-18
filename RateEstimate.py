#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-

########## Configuration #####################################################################
from triggersGroupMap.triggersGroupMap__frozen_2015_50ns_5e33_v2p1_HLT_V5 import *
from datasetCrossSections.datasetCrossSectionsPhys14 import *

folder = '/afs/cern.ch/user/s/sdonato/AFSwork/public/testNtuple/'
lumi =  5E33 # s-1cm-2
log = 2 # use log=2
multiprocess = 1           # number of processes
pileupFilter = True         # use pile-up filter?
pileupFilterGen = False     # use pile-up filter gen or L1?
useEMEnriched = True       # use plain QCD mu-enriched samples (Pt30to170)?
useMuEnriched = True       # use plain QCD EM-enriched samples (Pt30to170)?
evalHLTpaths = True        # evaluate HLT triggers rates?
evalHLTgroups = True       # evaluate HLT triggers groups rates  ?
#evalHLTtwopaths = True    # evaluate the correlation among the HLT trigger paths rates?
evalHLTtwogroups = False    # evaluate the correlation among the HLT trigger groups rates?
evalL1 = True              # evaluate L1 triggers rates?
label = "rates_V1"         # name of the output files
###############################################################################################

import ROOT
import time
import sys
from math import *
from os import walk
from os import mkdir
from scipy.stats import binom

EM_cut = "(!HLT_BCToEFilter_v1 && HLT_EmFilter_v1)"
Mu_cut = "MCmu3"

## modified square root to avoid error
def sqrtMod(x):
    if x>0: return sqrt(x)
    else: return 0

## not used (under development)
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

## not used (under development)
def test_CL(p,n):
    print  1-CL(p,n)[0]-CL(n-p,n)[1]
    print  1-CL(p,n)[1]-CL(n-p,n)[0]

## get the trigger list from the ntuples
def getTriggersListFromNtuple(chain,triggerListInNtuples):
            for leaf in chain.GetListOfLeaves():
               name = leaf.GetName()
               if (("HLT_" in name) or (evalL1 and ("L1_" in name))) and not ("Prescl" in name):
                triggerListInNtuples.append(name)

## set and fill totalEventsMatrix, passedEventsMatrix, rateTriggerTotal, squaredErrorRateTriggerTotal with zero
def setToZero(totalEventsMatrix,passedEventsMatrix,triggerAndGroupList,rateTriggerTotal,squaredErrorRateTriggerTotal) :
    for dataset in xsectionDatasets:
        totalEventsMatrix[dataset]=0
        for trigger in triggerAndGroupList:
            passedEventsMatrix[(dataset,trigger)]=0
    
    for trigger in triggerAndGroupList:
        rateTriggerTotal[trigger]=0
        squaredErrorRateTriggerTotal[trigger]=0

## read totalEventsMatrix and passedEventsMatrix and write a .csv file containing the number of events that passed the trigger
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

## read rateTriggerTotal and rateTriggerDataset and write a .csv file containing the trigger rates
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

## compare the trigger list from the ntuple and from triggersGroupMap*.py and print the difference
def CompareGRunVsGoogleDoc(datasetList,triggerList,folder):
    dirpath=''
    filenames=[]
    for dataset in datasetList:
        for (dirpath, dirnames, filenames) in walk(folder+'/'+dataset):
            if len(filenames)>0 and 'root' in filenames[0]: break
    
    if len(filenames) is 0:
        raise ValueError('No good file found in '+folder)
    
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

## given filepath, the filter string to use at the numerator and denominator, get the number of events that pass the triggers
def getEvents(input_):
        (filepath,filterString,denominatorString,withNegativeWeights) = input_
        passedEventsMatrix_={}
        ##try to open the file and get the TTree
        tree = None
        try:
            _file0 = ROOT.TFile.Open(filepath)
            tree=ROOT.gDirectory.Get("HltTree")
        except:
            pass
        
        ##if tree is defined, get totalEvents and passedEvents
        if (tree!=None): 
            totalEventsMatrix_ = tree.Draw("",denominatorString)
            if withNegativeWeights: totalEventsMatrix_= totalEventsMatrix_ - 2*tree.Draw("","(MCWeightSing<0)&&("+denominatorString+")") ##FIXME: MCWeightSing -> MCWeightSign
            for trigger in triggerAndGroupList:
                passedEventsMatrix_[trigger] = tree.Draw("",'('+getTriggerString[trigger]+')&&('+filterString+')')
                if withNegativeWeights: passedEventsMatrix_[trigger] = passedEventsMatrix_[trigger] - 2*tree.Draw("",'(MCWeightSing<0)&&('+getTriggerString[trigger]+')&&('+filterString+')') ##FIXME: MCWeightSing -> MCWeightSign
            
            _file0.Close()
        else:  ##if tree is not undefined/empty set enties to zero
            totalEventsMatrix_ = 0
            MCWeightSing
            for trigger in triggerAndGroupList:
                passedEventsMatrix_[trigger] = 0
        
        return passedEventsMatrix_,totalEventsMatrix_

## fill the matrixes of the number of events and the rates for each dataset and trigger
def fillMatrixAndRates(dataset,totalEventsMatrix,passedEventsMatrix,rateTriggerDataset,squaredErrorRateTriggerDataset):
    start = time.time()
    skip = False
    dirpath=''
    filenames=[]
    ## find the subdirectory containing the ROOT files
    for (dirpath, dirnames, filenames) in walk(folder+'/'+dataset):
       if len(filenames)>0 and 'root' in filenames[0]: break
    
    ## print an error if a dataset is missing
    if dirpath=='':
        print
        print '#'*80
        print '#'*10,"dataset=",dataset," not found!"
        print '#'*80
        skip = True
    
    ## get the cross section and the global rate of the dataset
    xsection = xsectionDatasets[dataset] #pb
    rateDataset [dataset] = lumi*xsection*1E-24/1E12 # [1b = 1E-24 cm^2, 1b = 1E12pb ]
    
    ## check if the dataset belong to the (anti) QCD EM/Mu enriched dataset lists or it contains negative weights
    isEMEnriched = False
    isMuEnriched = False
    isAntiEM = False
    isAntiMu = False
    withNegativeWeights = False
    
    if dataset in datasetEMEnrichedList:        isEMEnriched = True
    if dataset in datasetMuEnrichedList:        isMuEnriched = True
    if dataset in datasetAntiMuList:            isAntiMu = True
    if dataset in datasetAntiEMList:            isAntiEM = True
    if dataset in datasetNegWeightList:         withNegativeWeights = True
    
    filterString = '1'
    
    ## skip file if you have to
    if (not useMuEnriched) and isMuEnriched: skip = True
    if (not useEMEnriched) and isEMEnriched: skip = True
    
    ## apply PU filter
    if pileupFilter and ('QCD'in dirpath):
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
    
    ## print a log, only for one file per dataset
    if log>1:
        if not skip:
            print
            print '#'*10,"Dataset:",dataset,'#'*30
            print "Loading folder:",dirpath
            print "First file:",dirpath+'/'+filenames[0]
            print "nfiles =",len(filenames)
            print "total rate of dataset =",rateDataset [dataset]
            print "using numerator filter:",filterString
            print "using denominator filter:",denominatorString
            print "using negative weight? ",withNegativeWeights
        else:
            print
            print '#'*10,"Skipping ",dataset,'#'*30
    
    ## prepare the input for getEvents((filepath,filterString,denominatorString))
    inputs = []
    if not skip:
        for filename in filenames:
            inputs.append((dirpath+'/'+filename,filterString,denominatorString,withNegativeWeights))
    
    ## evaluate the number of events that pass the trigger with getEvents()
    if multiprocess>1:
        p = Pool(multiprocess)
        output = p.map(getEvents, inputs)
    
    ## get the output
    for input_ in inputs:
        if multiprocess>1: (passedEventsMatrix_,totalEventsMatrix_) = output[inputs.index(input_)]
        else: (passedEventsMatrix_,totalEventsMatrix_) = getEvents(input_)
        
        ##fill passedEventsMatrix[] and totalEventsMatrix[]
        totalEventsMatrix[dataset] += totalEventsMatrix_
        for trigger in triggerAndGroupList:
            passedEventsMatrix[(dataset,trigger)] += passedEventsMatrix_[trigger]
    
    ## do not crash if a dataset is missing!
    if totalEventsMatrix[dataset]==0:   totalEventsMatrix[dataset]=1
    
    ##fill passedEventsMatrix[] and totalEventsMatrix[]
    for trigger in triggerAndGroupList:
        rateTriggerDataset [(dataset,trigger)] = rateDataset[dataset]/totalEventsMatrix[dataset]*passedEventsMatrix[(dataset,trigger)]
        squaredErrorRateTriggerDataset [(dataset,trigger)] = rateDataset[dataset]*rateDataset[dataset]*passedEventsMatrix[(dataset,trigger)]/totalEventsMatrix[dataset]/totalEventsMatrix[dataset] # (rateDataset*sqrt(1.*passedEvents/nevents/nevents)) **2
    end = time.time()
    if log>1:
        if not skip: print "time(s) =",round((end - start),2)," total events=",totalEventsMatrix[dataset]," time per 10k events(s)=", round((end - start)*10000/totalEventsMatrix[dataset],2)

########## Main #####################################################################

## start the script
startGlobal = time.time() ## timinig stuff

## fill datasetList properly
datasetList=datasetQCD15+datasetList
datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList

## print a log
print
print "Using up to ", multiprocess ," processes."
print "Folder: ", folder
print "Luminosity: ", lumi
print "Use QCDEMEnriched? ", useEMEnriched
print "Use QCDMuEnriched? ", useMuEnriched
print "Evaluate L1 triggers rates? ", evalL1
print "Evaluate HLT triggers rates? ", evalHLTpaths
#print "Evaluate HLT triggers shared rates? ", evalHLTtwopaths
print "Evaluate HLT groups rates? ", evalHLTgroups
print "Evaluate HLT groups shared rates? ", evalHLTtwogroups
print "Pile-up filter: ",pileupFilter
if pileupFilter:
    print "Pile-up filter version: ",
    if pileupFilterGen:
        print "pt-hat MC truth (new)"
    else:
        print "leading L1 object (old)"

print

# load library for multiprocessing
if multiprocess>1: 
    from multiprocessing import Pool

### initialization ###
# fill triggerAndGroupList with the objects that you want to measure the rate (HLT+L1+HLTgroup+HLTtwogroup)
triggerAndGroupList=[]
if evalHLTpaths:        triggerAndGroupList=triggerAndGroupList+HLTList
if evalHLTgroups:       triggerAndGroupList=triggerAndGroupList+groupList
#if evalHLTtwopaths:     triggerAndGroupList=triggerAndGroupList+twoHLTsList
if evalHLTtwogroups:    triggerAndGroupList=triggerAndGroupList+twoGroupsList
if evalL1:              triggerAndGroupList=triggerAndGroupList+L1List

# fill triggerList with the trigger HLT+L1
triggerList=[]
if evalHLTpaths:        triggerList=triggerList+HLTList
if evalL1:              triggerList=triggerList+L1List

# define dictionaries
passedEventsMatrix = {}                 #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
totalEventsMatrix = {}                  #totalEventsMatrix[(dataset,trigger)] = total events of a dataset
rateDataset = {}                        #rateDataset[dataset] = rate of a dataset (xsect*lumi)
rateTriggerDataset = {}                 #rateTriggerDataset[(dataset,trigger)] = rate of a trigger in a dataset
squaredErrorRateTriggerDataset = {}     #squaredErrorRateTriggerDataset[(dataset,trigger)] = squared error on the rate
rateTriggerTotal = {}                   #rateTriggerTotal[(dataset,trigger)] = total rate of a trigger
squaredErrorRateTriggerTotal = {}       #squaredErrorRateTriggerTotal[trigger] = squared error on the rate
setToZero(totalEventsMatrix,passedEventsMatrix,triggerAndGroupList,rateTriggerTotal,squaredErrorRateTriggerTotal)  #fill all dictionaries with zero

## check trigger list in triggersGroupMap (ie. ~ Google doc), with trigger bits in ntuples (ie. GRun)
triggerList = CompareGRunVsGoogleDoc(datasetList,triggerList,folder)

## loop on dataset and fill matrix with event counts, rates, and squared errors
for dataset in datasetList:
    fillMatrixAndRates(dataset,totalEventsMatrix,passedEventsMatrix,rateTriggerDataset,squaredErrorRateTriggerDataset)

## evaluate the total rate with uncertainty for triggers and groups
for dataset in datasetList:
    for trigger in triggerAndGroupList:
            rateTriggerTotal[trigger] += rateTriggerDataset[(dataset,trigger)]
            squaredErrorRateTriggerTotal[trigger] += squaredErrorRateTriggerDataset[(dataset,trigger)]

filename = 'Results/'
filename += label
filename += "_"+triggerName
filename += "_"+str(lumi).replace("+","")
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



