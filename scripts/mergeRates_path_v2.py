# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../")
import os  
import csv
import math
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *
from triggersGroupMap.Menu_online_v3p1_V4 import *

Method = 1 #0: rate = count ; 1:HLT, rate = psNorm*count / LS*nLS ; 2:Zerobias, rate = 11245Hz * target nBunchs * nCount/total Event
LS = 23.31
PsNorm = 107*7.
nLS = 246-43+1
nLS = 0
ps_const = 11245.0*2200.0
for dataset in datasetList:
    xsection = xsectionDatasets[dataset]


def my_print(datasetList):
    for dataset in datasetList:
        print dataset
    print len(datasetList)

def getLS(input_dir, keyWord):
    tmp_dic = {}
    tmp_list = []
    for dataset in datasetList:
        tmp_dic[dataset] = 0
    wdir = input_dir
    for LS_file in os.listdir(wdir):
        tmp_file = open(wdir+LS_file,'r')
        for Line in tmp_file:
            line = Line.replace('\n','')
            if not line in tmp_list:
                tmp_list.append(line)
    for ls in tmp_list:
        for dataset in datasetList:
            if dataset in ls:
                tmp_dic[dataset] += 1 
    return tmp_dic


def mergeRates(input_dir,output_name,keyWord,AveWrite):
    wdir = input_dir
    
    ########## Merging the individual path rates
#    if L1write:
#        h1 = open(output_name[:-4]+'_L1.tsv', "w")
    rateList = []
    for i in range(2*len(datasetList)+7):
        rateList.append([]) #0 Prescale
    
    rateDataset = {}
    TotalEventsPerDataset = {}
    datasetListFromFile = []
    total_ps = 0
    ## fill datasetList properly
    for dataset in datasetList:
        datasetListFromFile.append(dataset)
        TotalEventsPerDataset[dataset] = 0

    
    Nlines = 0
    Nfiles = 0
    
    ### Looping over the individual .tsv files
    for rate_file in os.listdir(wdir):
        print rate_file
        if (keyWord in rate_file) :
#        if ("pu23to27rates_MC_v4p4_V1__frozen_2015_25ns14e33_v4p4_HLT_V1_2e33_PUfilterGen_matrixEvents.tsv" in rate_file) and not ("group" in rate_file):
            with open(wdir+rate_file) as tsvfile:
                print wdir+rate_file
                tsvreader = csv.reader(tsvfile, delimiter="\t")
                Nfiles += 1
                i = 0
                ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
                for line in tsvreader: 
    		    if "TotalEvents" in line[0]:
       			for k in xrange(0,len(datasetList)): 
                            print line[k+3]
                            TotalEventsPerDataset[datasetListFromFile[k]] += float(line[k+3])
                        print TotalEventsPerDataset
                        print line
                        print "*"*30
                        print len(line)
                        print "*"*30
                        continue
                    groupCheck = True
                    if (line[0]!='Path') and (line[0] not in rateList[1]):
                        if (groupCheck ): 
                            rateList[0].append(-1) # Need to be changed to prescales
                            rateList[1].append(line[0])
                            rateList[3].append(line[1])
                            rateList[2].append(line[2])
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+6].append(float(line[3*ii+3]))
                                rateList[2*ii+7].append(float(line[3*ii+5])**2)
                            tmp_count=0.0
                            tmp_error_sq=0.0
                            i += 1
                    elif (line[0]!='Path'):
                        if (groupCheck ):
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+6][i] += float(line[3*ii+3])
                                rateList[2*ii+7][i] += float(line[3*ii+5])**2
                            i += 1
                if (Nlines==0): Nlines = i
    
    print "Nfiles = ",Nfiles
    print "Nlines = ",Nlines
   
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
     
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
     
        return False
    
    TotalRateList = []
    TotalErrorList = []
   
    if Method==1:
        total_LS = 0
        for dataset in datasetList:
            if nLS_dic[dataset] == 0:
                rateDataset [dataset] = 0
            else:
                rateDataset [dataset] = PsNorm/(nLS_dic[dataset]*LS)
            total_LS += nLS_dic[dataset]
        rateDataset_total = PsNorm/(total_LS*LS)
    elif Method==2:
        rateDataset_total = 0
        for dataset in datasetList:
            rateDataset [dataset] = (ps_const/TotalEventsPerDataset[dataset])# [1b = 1E-24 cm^2, 1b = 1E12pb ]
            rateDataset_total += TotalEventsPerDataset[dataset]
            print rateDataset [dataset]
        rateDataset_total = ps_const/rateDataset_total

    elif Method==0:
        for dataset in datasetList:
            rateDataset[dataset]=1
            rateDataset_total = 1
    else:
        for dataset in datasetList:
            rateDataset[dataset]=0
            rateDataset_total = 0

    
    for j in xrange (0,Nlines):
        TotalRateList.append(0)
        TotalErrorList.append(0)
        for i in xrange(0,len(datasetList)):
                TotalRateList[j] += rateList[2*i+6][j]
                TotalErrorList[j] += rateList[2*i+7][j]
        TotalRateList[j] += total_ps
        TotalErrorList[j] = math.sqrt(math.fabs(TotalErrorList[j]))
    
    ### Filling up the new .tsv file with the content of the python list
    h = open(output_name, "w")
    if AveWrite:
        text_rate = 'Prescale\tPath\tDataset\tGroup\t\tTotal\t\t\tRate / #group\t\t\t'
    else:
        text_rate = 'Prescale\tPath\tDataset\tGroup\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
    text_rate += '\n'
    h.write(text_rate)

#    text_rate += "\tTotalEvents\t\t\t"
#    for dataset in datasetList:
#        text_rate += str(TotalEventsPerDataset[dataset])
#        text_rate += "\t\t\t"
#    text_rate = text_rate[:-1]+"\n"
#    h.write(text_rate)
    for j in xrange (0,Nlines):
        if rateList[1][j] in prescaleMap:
            rateList[0][j]=prescaleMap[rateList[1][j]][0]
    for j in xrange (0,Nlines):
        text_rate = ""
        text_rate += str(rateList[0][j])
        text_rate += "\t"
        text_rate += str(rateList[1][j])
        text_rate += "\t"
        text_rate += str(rateList[2][j])
        text_rate += "\t"
        text_rate += str(rateList[3][j])
        text_rate += "\t"

        text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
        text_rate += "\t+/-\t"
        text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
        text_rate += "\t"
        if AveWrite:
            tmp_group_len = len(rateList[3][j].split(','))
            if tmp_group_len <1: tmp_group_len = 1
            text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF/float(tmp_group_len))
            text_rate += "\t+/-\t"
            text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF/float(tmp_group_len))
            text_rate += "\t"
        for i in xrange(0,len(datasetList)):
            if rateList[0][j]==0:
                rate = 0.0
                error = 0.0
            else:
                rate = rateList[2*i+6][j]*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
                error = math.sqrt(rateList[2*i+7][j])*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
            text_rate += str(rate)
            text_rate += "\t+/-\t"
            text_rate += str(error)
            text_rate += "\t"
    
        text_rate = text_rate[:-1]+"\n"
        h.write(text_rate)
    h.close()

File_Factor=1.0
lumiSF=1.0
UnprescaledCount = True

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~
nLS_dic = {}
if Method == 1: 
    if nLS <= 0:
        nLS_dic = getLS("../ResultsBatch/ResultsBatch_LS/",'matrixEvents_HLTPhysics')
    else:
        for dataset in datasetList:
            nLS_dic[dataset] = nLS
print nLS_dic
#mergeRates("../ResultsBatch/ResultsBatch_Events/","../Results/output.tsv",'matrixEvents_HLTPhysics',True)
mergeRates("../ResultsBatch/ResultsBatch_Exclusive_Events/","../Results/output.excltrigger.tsv",'matrixEvents_Exclusive_trigger',True)


my_print(datasetList)

