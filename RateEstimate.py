#! /usr/bin/env python
# -*- coding: iso-8859-15 -*-

########## Configuration #####################################################################
from triggersGroupMap.HLT_Menu_v4p2_v6 import *
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *
from scripts.input_card import *

##### Adding an option to the code #####

from optparse import OptionParser
parser=OptionParser()

parser.add_option("-n","--number",dest="fileNumber",default=-1,type="int") # python file.py -n N => options.fileNumber is N
parser.add_option("-d","--dataset",dest="datasetName",default="all",type="str")
parser.add_option("-f","--name",dest="fileName",default="null",type="str")

(options,args)=parser.parse_args()

##### Other configurations #####

#folder = '/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Summer16_FlatPU28to62/HLTRates_v4p2_V2_1p25e34_MC_2017feb09J'
looping = False			# use looping method or not. Looping method can get group, dataset and stream rates from unprescaled Ntuples.
use_prescaled_ntuples = True	# this option will only work for looping == True.
multiprocess = 1		# 8 multiprocessing disbaled for now because of incompatibilities with the way the files are accessed. Need some development.
pileupMIN = 36			# get PU range for MC Ntuples.
pileupMAX = 40
pileupFilter = True		# use pile-up filter?
pileupFilterGen = True		# use pile-up filter gen or L1?
useEMEnriched = True		# use plain QCD mu-enriched samples (Pt30to170)?
useMuEnriched = True		# use plain QCD EM-enriched samples (Pt30to170)?
evalL1 = False			# evaluate L1 triggers rates?
evalHLTpaths = True		# evaluate HLT triggers rates?
eval_groups = True		# evaluate groups rates and global HLT and L1 rates
eval_primaryDatasets = True	# evaluate primary datasets rates
eval_primaryDatasets_core = False		# evaluate correlation rates between primary datasets
eval_Trigger_primaryDatasets_core = False	# evaluate correlation rates between primary dataset and trigger
eval_stream = False		# evaluate stream rates
evalPureRate_Group = False	# evaluate proportional group rates	
evalPureRate_Dataset = False	# evaluate proportional dataset rates
evalPureRate_Stream = False	# evaluate proportional stream rates
evalExclusive_Trigger = False	# evaluate exclusive trigger rates
evalExclusive_group = False	# evaluate exclusive group rates

use_json = False
json_file_name = '/afs/cern.ch/user/x/xgao/work/RateEstimate_16_12_2016/L1_accept/json_columns/PU_45to50_v4.2.2_PS_1.45e34.json'
label = "Data"         # name of the output files
runNo = "284035"           #if runNo='0', means code will run for all Run.
LS_min = '1'
LS_max = '73'            #default is 9999

isData = True
## log level
log = 2                     # use log=2
###############################################################################################

## filter to be used for QCD EM/Mu enriched
EM_cut = "(!HLT_BCToEFilter_v1 && HLT_EmFilter_v1)"# && HLT_EmGlobalFilter_v1)"
Mu_cut = "(HLT_MuFilter_v1)"#"(MCmu3 && HLT_MuFilter_v1)"

## filter to be used for pile-up filter
PUFilterGen = 'HLT_RemovePileUpDominatedEventsGen_v1'
PUFilterL1 = 'HLT_RemovePileUpDominatedEvents_v1'

##### Load lib #####

import ROOT
import time
import sys
from math import *
from os import walk
from os import mkdir
from scipy.stats import binom
import math
import datetime
import os
import shlex
import subprocess
import json

ROOT.TFormula.SetMaxima(10000,10000,10000) # Allows to extend the number of operators in a root TFormula. Needed to evaluate the .Draw( ,OR string) in the GetEvents function

##### Function definition #####

executable_eos = '/afs/cern.ch/project/eos/installation/cms/bin/eos.select'

def runCommand(commandLine):
    #sys.stdout.write("%s\n" % commandLine)
    args = shlex.split(commandLine)
    retVal = subprocess.Popen(args, stdout = subprocess.PIPE)
    return retVal

def check_json(runNo_in, LS):
    runNo = str(runNo_in)
    import json
    file1=open(json_file_name,'r')
    inp1={}
    text = ""
    for line1 in file1:
        text+=line1
    inp1 = json.loads(text)
    #print inp1.keys()
    if runNo in inp1:
        for part_LS in inp1[runNo]:
            if LS >= part_LS[0] and LS <= part_LS[1]:
                return True
    return False

def my_least_multiple(a_in,b_in):
    a = max(int(a_in),int(b_in))
    b = min(int(a_in),int(b_in))
    lm = a*b
    n=1
    while(n*a<a*b):
        if (n*a)%b==0:
            lm = n*a
            break
        n+=1
    return lm

def my_coreelation(list_in_1, list_in_2, dic_out, dic_out_err, weight_dic_in, typ_in_1, typ_in_2):
    for l1 in list_in_1:
        for l2 in list_in_2:
            weight = float(my_least_multiple(weight_dic_in[typ_in_1,l1],weight_dic_in[typ_in_2,l2]))
            dic_out[(l1,l2)] += 1/weight
            dic_out_err[(l1,l2)] += 1/(weight*weight)
         


def lsl(file_or_path,my_filelist):
    '''
    List EOS file/directory content, returning the information found in 'eos ls -l'.
    The output is a list of dictionaries with the following entries:
        permissions
        file
        modified
        size (in bytes)
    An exception of type IOError will be raised in case file/directory does not exist.
    '''

    directory = os.path.dirname(file_or_path)
    ls_command = runCommand('%s ls -l %s' % (executable_eos, file_or_path))

    stdout, stderr = ls_command.communicate()
    #print "stdout = ", stdout
    status = ls_command.returncode
    #print "status = ", status
    if status != 0:
        raise IOError("File/path = %s does not exist !!" % file_or_path)
    
    retVal = []
    for line in stdout.splitlines():
        fields = line.split()
        if len(fields) < 8:
            continue
        file_info = {
            'permissions' : fields[0],
            'size' : int(fields[4]),
            'file' : fields[8]
        }
        time_stamp = " ".join(fields[5:8])
        # CV: value of field[7] may be in format "hour:minute" or "year".
        #     if number contains ":" it means that value specifies hour and minute when file/directory was created
        #      and file/directory was created this year.
        if time_stamp.find(':') != -1:
            file_info['time'] = time.strptime(
                time_stamp + " " + str(datetime.datetime.now().year),
                "%b %d %H:%M %Y")
        else:
            file_info['time'] = time.strptime(time_stamp, "%b %d %Y")
        file_info['path'] = file_or_path
        #print "file_info = " % file_info
        retVal.append(file_info)
        my_filelist.append(file_info)
        tmp_path=file_info['path']+'/'+file_info['file']
        if not '.' in tmp_path[-5:]:
            isdir=True
        else:
            isdir=False
        #print "is dir: ", isdir
        #print "file_info =", file_info
        if isdir and not 'log' in tmp_path:
            lsl(file_info['path']+'/'+file_info['file'],my_filelist)
    return

def check_lsl(path, dataset):
    executable_eos = '/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
    directory = os.path.dirname(path)
    ls_command = runCommand('%s ls -l %s' % (executable_eos, path))

    stdout, stderr = ls_command.communicate()
    #print "stdout = ", stdout
    status = ls_command.returncode
    #print "status = ", status
    if status != 0:
        raise IOError("File/path = %s does not exist !!" % path)

    for line in stdout.splitlines():
        fields = line.split()
        if len(fields) < 8:
            continue
        file_info = {
            'permissions' : fields[0],
            'size' : int(fields[4]),
            'file' : fields[8]
        }
        if dataset in file_info['file']:return True
    return False

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

## get the prescale associated with a trigger from the ntuples
def getPrescaleListInNtuples():                                                                               
    prescales={}                                                                                                                   
  # take the first "hltbit" file                                                                                                   
    filenames = []                                                                                                                 
    if options.fileName == "null":
        for dataset in datasetList:
            for folder in folder_list:
                if check_lsl(folder, dataset):
                    eosDirContent = []
                    walking_folder = folder+"/"+dataset
                    lsl(walking_folder,eosDirContent)
                    for key in eosDirContent:
                        if (("failed" in str(key['path'])) or ("log" in str(key['file'])) or ("161108_170325" in str(key['path']))): continue
                        if (".root" in str(key['file'])):
                            filenames.append("root://eoscms//eos/cms"+str(key['path'])+'/'+str(key['file']))
                        if len(filenames)>0: break
                    if len(filenames)>0: break
            if len(filenames)>0: break
 
        if len(filenames)==0:                                                                                                          
            raise ValueError('No good file found in '+folder)                                                                          
        else:
            filename = filenames[0]
                                                                                                                                   
    else:
        filename = "root://eoscms//eos/cms"+options.fileName
    _file0 = ROOT.TFile.Open(filename)                                                                                 
    chain = ROOT.gDirectory.Get("HltTree")                                                                                         
                                                                                                                                   
    for leaf in chain.GetListOfLeaves():                                                                                           
        name = leaf.GetName()                                                                                                      
        if (("HLT_" in name) or (evalL1 and ("L1_" in name))) and not ("Prescl" in name):                                          
            trigger=name                                                                                                           
            i=0                                                                                                                    
            pname=name+'_Prescl'                                                                                                   
            for event in chain:                                                                                                    
                value=getattr(event,pname)                                                                                         
                if (i==2): break                                                                                                   
                i+=1                                                                                                               
            prescales[trigger]=value                                                                                               

    return prescales       

## set and fill totalEventsMatrix, passedEventsMatrix, rateTriggerTotal, squaredErrorRateTriggerTotal with zero
def setToZero(totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,triggerAndGroupList,triggerAndGroupList_core,passedEventsMatrix_Exclusive,WeightedErrorMatrix_Exclusive,rateTriggerTotal,squaredErrorRateTriggerTotal) :
    for dataset in xsectionDatasets:
        totalEventsMatrix[dataset]=0
        totalLSMatrix[dataset]=0
        for trigger in triggerAndGroupList:
            passedEventsMatrix[(dataset,trigger)]=0
            WeightedErrorMatrix[(dataset,trigger)]=0
            passedEventsMatrix_Pure[(dataset,trigger)]=0
            WeightedErrorMatrix_Pure[(dataset,trigger)]=0
            passedEventsMatrix_Exclusive[(dataset,trigger)]=0
            WeightedErrorMatrix_Exclusive[(dataset,trigger)]=0
        for trigger in triggerAndGroupList_core:
            passedEventsMatrix_Core[(dataset,trigger)]=0
            WeightedErrorMatrix_Core[(dataset,trigger)]=0
    
    for trigger in triggerAndGroupList:
        rateTriggerTotal[trigger]=0
        squaredErrorRateTriggerTotal[trigger]=0

## read totalEventsMatrix and passedEventsMatrix and write a .tsv file containing the number of events that passed the trigger
def writeMatrixLS(fileName,runlist):
    f = open(fileName, 'w')
    for runlist_part in runlist:
        f.write("%s\n"%(runlist_part))

def writeMatrixEvents(fileName,datasetList,triggerList,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix,writeGroup=False,writeDataset=False):
    f = open(fileName, 'w')
    text = 'Path\t' 
    if writeGroup: text += 'Group\t'
    if writeDataset: text += 'Primary dataset\t'
    for dataset in datasetList:
        datasetName = dataset[:-21]
        datasetName = datasetName.replace("-", "")
        datasetName = datasetName.replace("_", "")
        text +=  datasetName + '\t\t\t'

    text += '\n'
    text +=  'TotalEvents\t'
    if writeGroup: text += '\t'
    if writeDataset: text += '\t'
    for dataset in datasetList:
        text += str(totalEventsMatrix[dataset]) + '\t'

    for trigger in triggerList: 
        text += '\n'
        text +=  str(trigger)+'\t'
        if writeGroup:
            for group in triggersGroupMap[trigger]:
                if not group.isdigit(): text += group+','        
            text=text[:-1] ##remove the last comma
            text += '\t'
        if writeDataset :
            for dataset in triggersDatasetMap[trigger]: text += dataset+','
            text=text[:-1] ##remove the last comma
            text += '\t'       
 
        for dataset in datasetList:
            if options.datasetName=="all": text += str(passedEventsMatrix[(dataset,trigger)]) + '\t'
            elif dataset==options.datasetName: text += str(passedEventsMatrix[(dataset,trigger)]) + '\t±\t' + str(sqrtMod(WeightedErrorMatrix[(dataset,trigger)])) + '\t'
            else: text += str(0) + '\t±\t' + str(0) + '\t'

    f.write(text)
    f.close()

## read rateTriggerTotal and rateTriggerDataset and write a .tsv file containing the trigger rates
def writeMatrixRates(fileName,prescaleList,datasetList,rateTriggerDataset,rateTriggerTotal,triggerList,writeGroup=False,writeDataset=False):
    f = open(fileName, 'w')
    text = 'Prescale\t'
    text += 'Path\t'
    if writeGroup: text += 'Group\t'
    if writeDataset: text += 'Primary dataset\t'
    text += 'Total\t\t\t'
    for dataset in datasetList:
        datasetName = dataset
        #datasetName = dataset[:-21]
        #datasetName = datasetName.replace("-", "")
        #datasetName = datasetName.replace("_", "")
        text +=  datasetName + '\t\t\t'

    for trigger in triggerList:
        text += '\n'
        if (trigger not in groupList) and (trigger not in primaryDatasetList) and (trigger not in streamList):# and (trigger not in twoGroupsList):
            text += str(prescaleList[trigger])+'\t'
        else: text += ''+'\t'    
        text +=  trigger+'\t'
        if writeGroup:
            for group in triggersGroupMap[trigger]:
                if not group.isdigit(): text += group+','        
            text=text[:-1] ##remove the last comma
            text += '\t'
        if writeDataset and trigger not in L1List:
            for dataset in triggersDatasetMap[trigger]: text += dataset+','
            text=text[:-1] ##remove the last comma
            text += '\t'
        
        text += str(rateTriggerTotal[trigger])+'\t±\t'+str(sqrtMod(squaredErrorRateTriggerTotal[trigger]))+'\t'
        for dataset in datasetList:
            if options.datasetName=="all": text += str(rateTriggerDataset[(dataset,trigger)]) + '\t±\t' + str(sqrtMod(squaredErrorRateTriggerDataset[(dataset,trigger)])) + '\t'
            elif dataset==options.datasetName: text += str(rateTriggerDataset[(dataset,trigger)]) + '\t±\t' + str(sqrtMod(squaredErrorRateTriggerDataset[(dataset,trigger)])) + '\t'
            else: text += str(0) + '\t±\t' +str(0) + '\t'

    f.write(text)
    f.close()
    
## compare the trigger list from the ntuple and from triggersGroupMap*.py and print the difference
def CompareGRunVsGoogleDoc(datasetList,triggerList,isPrint = False):
    # take the first "hltbit" file
    local_run = True
    filenames = []
 
    filenames = []
    if options.fileName == "null":
        for dataset in datasetList:
            for folder in folder_list:
                if check_lsl(folder, dataset):
                    eosDirContent = []
                    walking_folder = folder+"/"+dataset
                    lsl(walking_folder,eosDirContent)
                    for key in eosDirContent:
                        if (("failed" in str(key['path'])) or ("log" in str(key['file']))): continue
                        if (".root" in str(key['file'])):
                            filenames.append("root://eoscms//eos/cms"+str(key['path'])+'/'+str(key['file']))
                        if len(filenames)>0: break
                    if len(filenames)>0: break
            if len(filenames)>0: break

        if len(filenames)==0:
            raise ValueError('No good file found in '+folder)
        else:
            filename = filenames[0]
    else: 
        filename = "root://eoscms//eos/cms"+options.fileName
    _file0 = ROOT.TFile.Open(filename)
    chain = ROOT.gDirectory.Get("HltTree")
    
    # get trigger bits and make a comparison with google DOC
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
    if(isPrint):
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
    return list(triggerList)

## given filepath, the filter string to use at the numerator and denominator, get the number of events that pass the triggers
def getEvents(input_):
    (filepath,filterString,denominatorString,withNegativeWeights,dataset) = input_
    print "Entered getEvents()",filepath
    passedEventsMatrix_={}
    WeightedErrorMatrix_={}
    passedEventsMatrix_Pure_={}
    WeightedErrorMatrix_Pure_={}
    passedEventsMatrix_Core_={}
    WeightedErrorMatrix_Core_={}
    passedEventsMatrix_Exclusive_={}
    WeightedErrorMatrix_Exclusive_={}

    for trigger in triggerAndGroupList:
        passedEventsMatrix_[trigger] = 0
        WeightedErrorMatrix_[trigger] = 0
        passedEventsMatrix_Pure_[trigger] = 0
        WeightedErrorMatrix_Pure_[trigger] = 0
        passedEventsMatrix_Exclusive_[trigger] = 0
        WeightedErrorMatrix_Exclusive_[trigger] = 0
    for trigger in triggerAndGroupList_core:
        passedEventsMatrix_Core_[trigger] = 0
        WeightedErrorMatrix_Core_[trigger] = 0

    #try to open the file and get the TTree
    tree = None
    _file0 = ROOT.TFile.Open(filepath)
    tree=ROOT.gDirectory.Get("HltTree")
    if not looping:
    ##### "Draw" method
        if (tree!=None): 
        # Creating aliases for HLT paths branches in the tree in order to reduce the length of the global OR string
            i = 0
            root_alias_dic = {}
            for leaf in tree.GetListOfLeaves():
                TriggerName = leaf.GetName()
                if (TriggerName in triggerList):
                    tree.SetAlias("T_"+str(i),TriggerName)
                    if not TriggerName in root_alias_dic:
                        root_alias_dic[TriggerName] = "T_"+str(i)
                    i += 1
    
            getTriggerString1={}
            for t in getTriggerString:
                getTriggerString1[t]=getTriggerString[t]
            for group in groupList:
                groupPathList = getTriggerString1[group].split('||')
                getTriggerString1[group] = '0'
                for triggerPath in groupPathList:
                    if triggerPath in triggerList:
                        triggerAlias = root_alias_dic[triggerPath] 
                        if getTriggerString1[group]!='0': getTriggerString1[group] += '||'+triggerAlias
                        else: getTriggerString1[group] = triggerAlias
    
            for Dataset in primaryDatasetList:
                datasetPathList = getTriggerString1[Dataset].split('||')
                getTriggerString1[Dataset] = '0'
                for triggerPath in datasetPathList:
                    if triggerPath in triggerList:
                        triggerAlias = root_alias_dic[triggerPath]
                        if getTriggerString1[Dataset]!='0': getTriggerString1[Dataset] += '||'+triggerAlias
                        else: getTriggerString1[Dataset] = triggerAlias

            for stream in streamList:
                streamPathList = getTriggerString1[stream].split('||')
                getTriggerString1[stream] = '0'
                for triggerPath in streamPathList:
                    if triggerPath in triggerList:
                        triggerAlias = root_alias_dic[triggerPath]
                        if getTriggerString1[stream]!='0': getTriggerString1[stream] += '||'+triggerAlias
                        else: getTriggerString1[stream] = triggerAlias
#                print getTriggerString1[stream]
#                print "*"*50

        #if tree is defined, get totalEvents and passedEvents
        if (tree!=None): 
            if isData:
                totalEventsMatrix_ = tree.Draw("",denominatorString) 
                if withNegativeWeights: totalEventsMatrix_= totalEventsMatrix_ - 2*tree.Draw("",'(MCWeightSign<0)&&('+denominatorString+')')
                for trigger in triggerAndGroupList:
                    passedEventsMatrix_[trigger] = tree.Draw("",'('+getTriggerString1[trigger]+')&&('+filterString+')')
                    if withNegativeWeights: passedEventsMatrix_[trigger] = passedEventsMatrix_[trigger] - 2*tree.Draw("",'(MCWeightSign<0)&&('+getTriggerString1[trigger]+')&&('+filterString+')')
            else:
                print filterString
                print denominatorString
                totalEventsMatrix_ = tree.Draw("",'('+denominatorString+')&&(NPUTrueBX0<='+str(pileupMAX)+')&&(NPUTrueBX0>='+str(pileupMIN)+')')
                if withNegativeWeights: totalEventsMatrix_= totalEventsMatrix_ - 2*tree.Draw("",'(MCWeightSign<0)&&('+denominatorString+')&&(NPUTrueBX0<='+str(pileupMAX)+')&&(NPUTrueBX0>='+str(pileupMIN)+')')
                for trigger in triggerAndGroupList:
                    passedEventsMatrix_[trigger] = tree.Draw("",'('+getTriggerString1[trigger]+')&&('+filterString+')&&(NPUTrueBX0<='+str(pileupMAX)+')&&(NPUTrueBX0>='+str(pileupMIN)+')')
                    if withNegativeWeights: passedEventsMatrix_[trigger] = passedEventsMatrix_[trigger] - 2*tree.Draw("",'(MCWeightSign<0)&&('+getTriggerString1[trigger]+')&&('+filterString+')&&(NPUTrueBX0<='+str(pileupMAX)+')&&(NPUTrueBX0>='+str(pileupMIN)+')')

            # if is data, calculate number of Lumi Section processed
            if (isData and tree!=None):
                print "%s is data, try to get nLS %s"%("#"*20,"#"*20)
                n_processed = 0
                Total_LS = 0
                N = tree.GetEntries()
                for event in tree:
                    if n_processed%(N/5)==0: print "\r{0:.1f} %".format(100*float(n_processed)/float(N))
                    n_processed += 1
                    if (int(runNo) != 0) and int(getattr(event,'Run')) != int(runNo):continue
                    if (int(runNo) != 0) and (int(getattr(event,'LumiBlock')) < int(LS_min) or int(getattr(event,'LumiBlock')) > int(LS_max)):continue
                    runnr = int(getattr(event,'Run'))
                    runls = int(getattr(event,'LumiBlock'))
                    runstr = str((dataset,runnr,runls))
                    if not runstr in runlist:
                        runlist.append(runstr)
                        Total_LS += 1
                totalLSMatrix_ = Total_LS
    
                _file0.Close()
        else:  #if tree is not undefined/empty set enties to zero
            totalEventsMatrix_ = 0
            totalLSMatrix_ = 0 
            for trigger in triggerAndGroupList:
                passedEventsMatrix_[trigger] = 0
    
    ##### Looping method
    else:
        #if tree is defined, get totalEvents and passedEvents
        if (tree!=None):
            N = tree.GetEntries()
            i = 0
            # Looping over the events to compute the rates
            n_processed = 0
            print "Nevents =",N
            Total_count = 0
            Total_LS = 0
            runstr = ""
            for event in tree:
                if n_processed%(N/50)==0: print "\r{0:.1f} %".format(100*float(n_processed)/float(N))
                n_processed += 1 
                if use_json:
                   if (not check_json(int(getattr(event,'Run')),int(getattr(event,'LumiBlock')))):continue
                else :
                    if (int(runNo) != 0) and int(getattr(event,'Run')) != int(runNo):continue
                    if (int(runNo) != 0) and (int(getattr(event,'LumiBlock')) < int(LS_min) or int(getattr(event,'LumiBlock')) > int(LS_max)):continue
                Total_count +=1
                runnr = int(getattr(event,'Run'))
                runls = int(getattr(event,'LumiBlock'))
                runstr = str((dataset,runnr,runls))
                if not runstr in runlist:
                    runlist.append(runstr)
                    Total_LS += 1
                if not isData: 
                    PUevent = getattr(event,"NPUTrueBX0")
                    if (PUevent>pileupMAX or PUevent<pileupMIN): 
                        continue
                #print runlist
                TriggerCount = 0
                stringMemory = ""
                tmp_PureWeight = 0
                count_pure_trigger = 0
                count_pure_group = 0
                count_pure_dataset = 0
                count_pure_stream = 0
                count_exclusive_trigger = 0
                corelation_dataset_list = []
                corelation_trigger_list = []
                corelation_group_list = []
                PureCount_dic = {}
                #print "Event start"
                for trigger in triggerAndGroupList:
                    #print "start : %s"%trigger
                    if getTriggerString[trigger] == '0':continue
                    if trigger in corelation_datasetList:continue
                    if trigger in groupList: 
                        triggerInGroupList = getTriggerString[trigger].split('||')
                        tempCount = 1e+10 
                        for path in triggerInGroupList:     
                            if not (path in triggerList):continue
                            if (path not in prescaleMap.keys()) or int(prescaleMap[path][0])==0 or prescaleMap[path][0]=='' or 'DST_' in path or 'AlCa_' in path: continue 
                            TriggerCount = getattr(event,path) 
                            if TriggerCount and (int(prescaleMap[path][0])<tempCount): tempCount = int(prescaleMap[path][0])
                        if tempCount==1e+10: continue
                        passedEventsMatrix_[trigger] += 1/float(tempCount)
                        WeightedErrorMatrix_[trigger] += (1/float(tempCount))*(1/float(tempCount))
                        if "All" in trigger or "type" in trigger: continue
                        if use_prescaled_ntuples:
                            PureCount_dic[("group",trigger)] = 1.0
                        else:
                            PureCount_dic[("group",trigger)] = tempCount
                        count_pure_group += 1
                        corelation_group_list.append(trigger)
                    elif trigger in primaryDatasetList:
                        triggerInDatasetList = getTriggerString[trigger].split('||')
                        tempCount = 1e+10
                        for path in triggerInDatasetList:
                            if not (path in triggerList):continue
                            if (path not in prescaleMap.keys()) or int(prescaleMap[path][0])==0 or prescaleMap[path][0]=='': continue
                            TriggerCount = getattr(event,path)
                            if TriggerCount and (int(prescaleMap[path][0])<tempCount): tempCount = int(prescaleMap[path][0])
                        if tempCount==1e+10: continue
                        passedEventsMatrix_[trigger] += 1/float(tempCount)
                        WeightedErrorMatrix_[trigger] += (1/float(tempCount))*(1/float(tempCount))
                        if trigger in pure_primaryDatasetList:
                            if use_prescaled_ntuples:
                                PureCount_dic[("dataset",trigger)] = 1.0
                            else:
                                PureCount_dic[("dataset",trigger)] = tempCount
                            count_pure_dataset += 1
                            corelation_dataset_list.append(trigger)
                    elif trigger in streamList:
                        triggerInStreamList = getTriggerString[trigger].split('||')
                        tempCount = 1e+10
                        for path in triggerInStreamList:
                            if not (path in triggerList):continue
                            if (path not in prescaleMap.keys()) or int(prescaleMap[path][0])==0 or prescaleMap[path][0]=='': continue
                            TriggerCount = getattr(event,path)
                            if TriggerCount and (int(prescaleMap[path][0])<tempCount): tempCount = int(prescaleMap[path][0])
                        if tempCount==1e+10: continue
                        passedEventsMatrix_[trigger] += 1/float(tempCount)
                        WeightedErrorMatrix_[trigger] += (1/float(tempCount))*(1/float(tempCount))
                        if trigger in pure_streamList:
                            if use_prescaled_ntuples:
                                PureCount_dic[("stream",trigger)] = 1.0
                            else:
                                PureCount_dic[("stream",trigger)] = tempCount
                            count_pure_stream += 1
                    else:
                        if (trigger not in prescaleMap.keys()) or int(prescaleMap[trigger][0])==0 or prescaleMap[trigger][0]=='': continue 
                        else: 
                            TriggerCount = getattr(event,trigger)
                            if (TriggerCount==1):
                                passedEventsMatrix_[trigger] += 1/float(prescaleMap[trigger][0])
                                WeightedErrorMatrix_[trigger] += (1/float(prescaleMap[trigger][0]))*(1/float(prescaleMap[trigger][0]))
                                if use_prescaled_ntuples:
                                    PureCount_dic[("trigger",trigger)] = 1.0
                                else:
                                    PureCount_dic[("trigger",trigger)] = float(prescaleMap[trigger][0])
                                corelation_trigger_list.append(trigger)
                                if trigger in pure_triggerList:
                                    count_exclusive_trigger += 1
                for (typ,trigger) in PureCount_dic:
                    #Exclusive rate for group, dataset, trigger:
                    if evalExclusive_group:
                        if typ == "group" and count_pure_group == 1:
                            tempCount = PureCount_dic[(typ,trigger)]
                            passedEventsMatrix_Exclusive_[trigger] += 1/float(tempCount)
                            WeightedErrorMatrix_Exclusive_[trigger] += (1/float(tempCount))*(1/float(tempCount))
                    if evalExclusive_Trigger:
                        if typ == "trigger" and count_exclusive_trigger == 1 and (trigger in pure_triggerList):
                            tempCount = PureCount_dic[(typ,trigger)]
                            passedEventsMatrix_Exclusive_[trigger] += 1/float(tempCount)
                            WeightedErrorMatrix_Exclusive_[trigger] += (1/float(tempCount))*(1/float(tempCount))

                    if typ == "trigger":	continue#tmp_PureWeight=count_pure_trigger
                    if typ == "group":		tmp_PureWeight=count_pure_group 
                    if typ == "dataset":	tmp_PureWeight=count_pure_dataset 
                    if typ == "stream":		tmp_PureWeight=count_pure_stream 
                    if tmp_PureWeight == 0:tmp_PureWeight=1
                    tempCount = PureCount_dic[(typ,trigger)]*tmp_PureWeight
                    passedEventsMatrix_Pure_[trigger] += 1/float(tempCount)
                    WeightedErrorMatrix_Pure_[trigger] += (1/float(tempCount))*(1/float(tempCount))
       
                    #if typ == "group": print "N=%d,  %s : %0.4f,  %0.4f"%(tmp_PureWeight,trigger, 1/float(PureCount_dic[(typ,trigger)]),1/float(tempCount))
                    #if typ == "dataset": print "N=%d,  %s : %0.4f,  %0.4f"%(tmp_PureWeight,trigger, 1/float(PureCount_dic[(typ,trigger)]),1/float(tempCount))
                    #if typ == "stream": print "N=%d,  %s : %0.4f,  %0.4f"%(tmp_PureWeight,trigger, 1/float(PureCount_dic[(typ,trigger)]),1/float(tempCount))

                if eval_primaryDatasets_core:
                    my_coreelation(corelation_dataset_list, corelation_dataset_list, passedEventsMatrix_Core_, WeightedErrorMatrix_Core_, PureCount_dic, "dataset", "dataset")
                if eval_Trigger_primaryDatasets_core:
                    my_coreelation(corelation_trigger_list, corelation_dataset_list, passedEventsMatrix_Core_, WeightedErrorMatrix_Core_, PureCount_dic, "trigger", "dataset")
            totalEventsMatrix_ = Total_count
            totalLSMatrix_ = Total_LS

        else:  #if chain is not undefined/empty set entries to zero
            totalEventsMatrix_ = 0
            totalLSMatrix_ = 0 
            for trigger in triggerAndGroupList:
                passedEventsMatrix_[trigger] = 0
                passedEventsMatrix_Pure[trigger] = 0
                passedEventsMatrix_Exclusive[trigger] = 0
            for trigger in triggerAndGroupList_core:
                passedEventsMatrix_Core_[trigger] = 0

    return passedEventsMatrix_,totalEventsMatrix_,totalLSMatrix_,WeightedErrorMatrix_,passedEventsMatrix_Pure_,WeightedErrorMatrix_Pure_,passedEventsMatrix_Core_,WeightedErrorMatrix_Core_,passedEventsMatrix_Exclusive_,WeightedErrorMatrix_Exclusive_

## fill the matrixes of the number of events and the rates for each dataset and trigger
def fillMatrixAndRates(dataset,totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,rateTriggerDataset,squaredErrorRateTriggerDataset):
    print "Entered fillMatrixAndRates()"
    start = time.time()
    skip = False

    ## find the subdirectory containing the ROOT files
    dirpath=''
    filenames=[]
    walking_folder = ""
    if options.fileName == "null":
        for folder in folder_list:
            if check_lsl(folder, dataset):
                walking_folder = folder+"/"+dataset
                eosDirContent=[]
                lsl(walking_folder,eosDirContent)
                for key in eosDirContent:
                    if (("failed" in str(key['path'])) or ("log" in str(key['file'])) or ("161108_170325" in str(key['path']))): continue
                    if (".root" in str(key['file'])):
                        filenames.append("root://eoscms//eos/cms"+str(key['path'])+'/'+str(key['file']))
                        dirpath = "root://eoscms//eos/cms"+walking_folder
    else:
        filenames.append("root://eoscms//eos/cms"+options.fileName)
        dirpath = "root://eoscms//eos/cms"+options.fileName
        print options.fileName
        print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

    ## print an error if a dataset is missing
    if (dirpath=='' or (len(filenames)<options.fileNumber)) and (options.fileName=="null"):
            print
            print '#'*80
            print '#'*10,"dataset=",dataset," not found!"
            print '#'*80
            skip = True
    
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
    if isData and runNo!='0':
        filterString+="&&(Run=="+runNo+")"   
        if LS_min !='0':
            filterString+="&&(LumiBlock>="+LS_min+")&&(LumiBlock<="+LS_max+")"
 
    ## skip file if you have to
    if (not useMuEnriched) and isMuEnriched: skip = True
    if (not useEMEnriched) and isEMEnriched: skip = True
    
    ## apply PU filter
    if pileupFilter and ('QCD'in dataset):
        if pileupFilterGen: filterString += '&&'+PUFilterGen
        else: filterString += '&&'+PUFilterL1
    
    ## if useEMEnriched, apply AntiEM cut 
    if useEMEnriched and isAntiEM: filterString += '&& !'+EM_cut
    
    ## if useMuEnriched, apply AntiMu cut
    if useMuEnriched and isAntiMu: filterString += '&& !'+Mu_cut
    
    denominatorString = '1'
    if isData and runNo!='0':
        denominatorString+="&&(Run=="+runNo+")"   
        if LS_min !='0':
            denominatorString+="&&(LumiBlock>="+LS_min+")&&(LumiBlock<="+LS_max+")"
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
            print "Loading folder:",walking_folder
            print "First file:",filenames[0]
            print "nfiles =",len(filenames)
            print "using numerator filter:",filterString
            print "using denominator filter:",denominatorString
            print "using negative weight? ",withNegativeWeights
        else:
            print
            print '#'*10,"Skipping ",dataset,'#'*30
    
    if not skip:
        ## prepare the input for getEvents((filepath,filterString,denominatorString))
        inputs = []
        if(options.fileName != "null"):
            filename = filenames[0]
            print "file %s added to inputs -f"%(filename)
            inputs.append((filename,filterString,denominatorString,withNegativeWeights,dataset))
        elif(options.fileNumber > 0):
            filename = filenames[options.fileNumber-1]
            print "file ",options.fileNumber," (",filename,") added to inputs"
            inputs.append((filename,filterString,denominatorString,withNegativeWeights,dataset))
        else:
            print "All files (%d in total) added to inputs"%(len(filenames))
            for i in range(len(filenames)):
                filename = filenames[i]
                inputs.append((filename,filterString,denominatorString,withNegativeWeights,dataset))
 
        ## evaluate the number of events that pass the trigger with getEvents()
        if multiprocess>1:
            p = Pool(multiprocess)
            output = p.map(getEvents, inputs)
    
        ## get the output
        for input_ in inputs:
            if multiprocess>1: (passedEventsMatrix_,totalEventsMatrix_,totalLSMatrix_,WeightedErrorMatrix_,passedEventsMatrix_Pure_,WeightedErrorMatrix_Pure_,passedEventsMatrix_Core_,WeightedErrorMatrix_Core_,passedEventsMatrix_Exclusive_,WeightedErrorMatrix_Exclusive_) = output[inputs.index(input_)]
            else: (passedEventsMatrix_,totalEventsMatrix_,totalLSMatrix_,WeightedErrorMatrix_,passedEventsMatrix_Pure_,WeightedErrorMatrix_Pure_,passedEventsMatrix_Core_,WeightedErrorMatrix_Core_,passedEventsMatrix_Exclusive_,WeightedErrorMatrix_Exclusive_) = getEvents(input_)
        
            ##fill passedEventsMatrix[] and totalEventsMatrix[]
            totalEventsMatrix[dataset] += totalEventsMatrix_
            totalLSMatrix[dataset] += totalLSMatrix_
            for trigger in triggerAndGroupList:
                passedEventsMatrix[(dataset,trigger)] += passedEventsMatrix_[trigger]
                WeightedErrorMatrix[(dataset,trigger)] += WeightedErrorMatrix_[trigger]

                passedEventsMatrix_Pure[(dataset,trigger)] += passedEventsMatrix_Pure_[trigger]
                WeightedErrorMatrix_Pure[(dataset,trigger)] += WeightedErrorMatrix_Pure_[trigger]

                passedEventsMatrix_Exclusive[(dataset,trigger)] += passedEventsMatrix_Exclusive_[trigger]
                WeightedErrorMatrix_Exclusive[(dataset,trigger)] += WeightedErrorMatrix_Exclusive_[trigger]
              
            for trigger in triggerAndGroupList_core:
                passedEventsMatrix_Core[(dataset,trigger)] += passedEventsMatrix_Core_[trigger]
                WeightedErrorMatrix_Core[(dataset,trigger)] += WeightedErrorMatrix_Core_[trigger]
        
    ## do not crash if a dataset is missing!
    else:
        totalEventsMatrix[dataset]=1
        for trigger in triggerAndGroupList:
                passedEventsMatrix[(dataset,trigger)] = 0

        rateTriggerDataset [(dataset,trigger)] = 0
        squaredErrorRateTriggerDataset [(dataset,trigger)] = 0

    end = time.time()
    if log>1:
        if not skip: print "time(s) =",round((end - start),2)," total events=",totalEventsMatrix[dataset]," total Lumi Section=",totalLSMatrix[dataset]," time per 10k events(s)=", round((end - start)*10000/totalEventsMatrix[dataset],2)

########## Main #####################################################################

## start the script
startGlobal = time.time() ## timinig stuff

## fill datasetList properly
datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList

## print a log
print
print "is Data:",isData
print "Using up to ", multiprocess ," processes."
print "Folder list: "
for folder in folder_list:
    print folder
print "Use QCDEMEnriched? ", useEMEnriched
print "Use QCDMuEnriched? ", useMuEnriched
print "Evaluate L1 triggers rates? ", evalL1
print "Evaluate HLT triggers rates? ", evalHLTpaths
#print "Evaluate HLT triggers shared rates? ", evalHLTtwopaths
print "Evaluate HLT groups rates? ", eval_groups
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
triggerAndGroupList_core=[]
#if not evalL1: groupList.remove('L1')
#if not evalHLTpaths : groupList.remove('All_HLT')
if evalHLTpaths:
    HLTList = CompareGRunVsGoogleDoc(datasetList,HLTList)
    triggerAndGroupList=triggerAndGroupList+HLTList
if evalL1:              
    L1List = CompareGRunVsGoogleDoc(datasetList,L1List)
    triggerAndGroupList=triggerAndGroupList+L1List

if eval_primaryDatasets: 
    triggerAndGroupList=triggerAndGroupList+primaryDatasetList
if eval_stream: 
    triggerAndGroupList=triggerAndGroupList+streamList
if eval_groups:       
    triggerAndGroupList=triggerAndGroupList+groupList
#if evalHLTtwopaths:     triggerAndGroupList=triggerAndGroupList+twoHLTsList
if eval_primaryDatasets_core: 
    triggerAndGroupList_core=triggerAndGroupList_core+corelation_datasetList
if eval_Trigger_primaryDatasets_core: 
    triggerAndGroupList_core=triggerAndGroupList_core+corelation_trigger_datasetList
#if evalL1:              triggerAndGroupList=triggerAndGroupList+L1List


# fill triggerList with the trigger HLT+L1
#triggerList=[]
#if evalHLTpaths:        triggerList=triggerList+HLTList
#if evalL1:              triggerList=triggerList+L1List
## check trigger list in triggersGroupMap (ie. ~ Google doc), with trigger bits in ntuples (ie. GRun)
if evalHLTpaths or evalL1: triggerList = CompareGRunVsGoogleDoc(datasetList,triggerList)
if evalExclusive_Trigger: pure_triggerList = CompareGRunVsGoogleDoc(datasetList,pure_triggerList)


# define dictionaries
passedEventsMatrix = {}                 #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
WeightedErrorMatrix = {}
passedEventsMatrix_Pure = {}                 #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
WeightedErrorMatrix_Pure = {}
passedEventsMatrix_Core = {}                 #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
WeightedErrorMatrix_Core = {}
passedEventsMatrix_Exclusive = {}                 #passedEventsMatrix[(dataset,trigger)] = events passed by a trigger in a dataset
WeightedErrorMatrix_Exclusive = {}

totalEventsMatrix = {}                  #totalEventsMatrix[(dataset,trigger)] = total events of a dataset
totalLSMatrix = {}                      #totalEventsMatrix[(dataset,trigger)] = total lumi section of a dataset
rateTriggerDataset = {}                 #rateTriggerDataset[(dataset,trigger)] = rate of a trigger in a dataset
squaredErrorRateTriggerDataset = {}     #squaredErrorRateTriggerDataset[(dataset,trigger)] = squared error on the rate
rateTriggerTotal = {}                   #rateTriggerTotal[(dataset,trigger)] = total rate of a trigger
squaredErrorRateTriggerTotal = {}       #squaredErrorRateTriggerTotal[trigger] = squared error on the rate

runlist = []

setToZero(totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,triggerAndGroupList,triggerAndGroupList_core,passedEventsMatrix_Exclusive,WeightedErrorMatrix_Exclusive,rateTriggerTotal,squaredErrorRateTriggerTotal)  #fill all dictionaries with zero

## create a list with prescales associated to each HLT/L1 trigger path
prescaleList = {}               # prescaleTriggerTotal[trigger] = prescale from Ntuple                                             
prescaleList = getPrescaleListInNtuples()                                                                                             
#print prescaleList       

#print triggerAndGroupList
#print 1/0

## loop on dataset and fill matrix with event counts, rates, and squared errors
for dataset in datasetList:
    if options.fileName =="null": 
        if options.datasetName=="all":
            fillMatrixAndRates(dataset,totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,rateTriggerDataset,squaredErrorRateTriggerDataset)
        elif dataset==options.datasetName:
            fillMatrixAndRates(dataset,totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,rateTriggerDataset,squaredErrorRateTriggerDataset)
            break
    else:
        if dataset in options.fileName:
            fillMatrixAndRates(dataset,totalEventsMatrix,totalLSMatrix,passedEventsMatrix,WeightedErrorMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure,passedEventsMatrix_Core,WeightedErrorMatrix_Core,rateTriggerDataset,squaredErrorRateTriggerDataset)
            break

directoryname = 'ResultsBatch/'
filename = ''
filename += label
filename += "_"+triggerName
if pileupFilter:
    if pileupFilterGen:filename += '_PUfilterGen'
    else:filename += '_PUfilterL1'

if useEMEnriched: filename += '_EMEn'
if useMuEnriched: filename += '_MuEn'


try:
    #mkdir("ResultsBatch_Parking2_Parking3")
    if not os.path.exists(directoryname+"ResultsBatch_LS"): os.makedirs(directoryname+"ResultsBatch_LS")
    if not os.path.exists(directoryname+"ResultsBatch_Events"): os.makedirs(directoryname+"ResultsBatch_Events")
    if not os.path.exists(directoryname+"ResultsBatch_groupEvents"): os.makedirs(directoryname+"ResultsBatch_groupEvents")
    if not os.path.exists(directoryname+"ResultsBatch_primaryDatasetEvents"): os.makedirs(directoryname+"ResultsBatch_primaryDatasetEvents")
    if not os.path.exists(directoryname+"ResultsBatch_streamEvents"): os.makedirs(directoryname+"ResultsBatch_streamEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Pure_groupEvents"): os.makedirs(directoryname+"ResultsBatch_Pure_groupEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Pure_primaryDatasetEvents"): os.makedirs(directoryname+"ResultsBatch_Pure_primaryDatasetEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Pure_streamEvents"): os.makedirs(directoryname+"ResultsBatch_Pure_streamEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Core_primaryDatasetEvents"): os.makedirs(directoryname+"ResultsBatch_Core_primaryDatasetEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Core_TriggerDatasetEvents"): os.makedirs(directoryname+"ResultsBatch_Core_TriggerDatasetEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Exclusive_Events"): os.makedirs(directoryname+"ResultsBatch_Exclusive_Events")
    if not os.path.exists(directoryname+"ResultsBatch_Exclusive_groupEvents"): os.makedirs(directoryname+"ResultsBatch_Exclusive_groupEvents")
    if not os.path.exists(directoryname+"ResultsBatch_Exclusive_primaryDatasetEvents"): os.makedirs(directoryname+"ResultsBatch_Exclusive_primaryDatasetEvents")
except:
    pass

### write files with events count
writeMatrixLS(directoryname+'ResultsBatch_LS/'+filename+'_matrixEvents_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',runlist)
###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if evalL1: writeMatrixEvents(directoryname+'ResultsBatch_Events/'+filename+'_L1_matrixEvents_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,L1List,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix,True,True)
if evalHLTpaths: writeMatrixEvents(directoryname+'ResultsBatch_Events/'+filename+'_matrixEvents_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,HLTList,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix,True,True)

if eval_primaryDatasets: writeMatrixEvents(directoryname+'ResultsBatch_primaryDatasetEvents/'+filename+'_matrixEvents_primaryDataset_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,primaryDatasetList,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix)
if eval_groups: writeMatrixEvents(directoryname+'ResultsBatch_groupEvents/'+filename+'_matrixEvents_groups_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,groupList,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix)
if eval_stream: writeMatrixEvents(directoryname+'ResultsBatch_streamEvents/'+filename+'_matrixEvents_stream_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,streamList,totalEventsMatrix,passedEventsMatrix,WeightedErrorMatrix)

if evalPureRate_Group: writeMatrixEvents(directoryname+'ResultsBatch_Pure_groupEvents/'+filename+'_matrixEvents_Pure_groups_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,groupList,totalEventsMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure)
if evalPureRate_Dataset: writeMatrixEvents(directoryname+'ResultsBatch_Pure_primaryDatasetEvents/'+filename+'_matrixEvents_Pure_primaryDataset_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,pure_primaryDatasetList,totalEventsMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure)
if evalPureRate_Stream: writeMatrixEvents(directoryname+'ResultsBatch_Pure_streamEvents/'+filename+'_matrixEvents_Pure_Stream_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,streamList,totalEventsMatrix,passedEventsMatrix_Pure,WeightedErrorMatrix_Pure)

if evalExclusive_Trigger: writeMatrixEvents(directoryname+'ResultsBatch_Exclusive_Events/'+filename+'_matrixEvents_Exclusive_trigger_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,pure_triggerList,totalEventsMatrix,passedEventsMatrix_Exclusive,WeightedErrorMatrix_Exclusive,True,True)
if evalExclusive_group: writeMatrixEvents(directoryname+'ResultsBatch_Exclusive_groupEvents/'+filename+'_matrixEvents_Exclusive_groups_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,groupList,totalEventsMatrix,passedEventsMatrix_Exclusive,WeightedErrorMatrix_Exclusive)

if eval_primaryDatasets_core: writeMatrixEvents(directoryname+'ResultsBatch_Core_primaryDatasetEvents/'+filename+'_matrixEvents_Core_primaryDataset_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,corelation_datasetList,totalEventsMatrix,passedEventsMatrix_Core,WeightedErrorMatrix_Core)
if eval_Trigger_primaryDatasets_core: writeMatrixEvents(directoryname+'ResultsBatch_Core_TriggerDatasetEvents/'+filename+'_matrixEvents_Core_TriggerDataset_'+str(options.datasetName)+'_'+str(options.fileNumber)+'.tsv',datasetList,corelation_trigger_datasetList,totalEventsMatrix,passedEventsMatrix_Core,WeightedErrorMatrix_Core)



## print timing
endGlobal = time.time()
totalEvents = 0
totalLS = 0
for dataset in datasetList: 
    totalEvents+=totalEventsMatrix[dataset]
    totalLS+=totalLSMatrix[dataset]
print
print "Total Time=",round((endGlobal - startGlobal),2)," Events=",totalEvents," Lumi Section=",totalLS," TimePer10kEvent=", round((endGlobal - startGlobal)*10000/totalEvents,2)



