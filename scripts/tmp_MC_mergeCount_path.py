# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../")
import os  
import csv
import math
from triggersGroupMap.HLT_Menu_v4p2_v6 import *
from datasetCrossSections.datasetCrossSectionsSummer16 import *

lumi = 1.103E34


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


def mergeRates(input_dir_list,output_name,keyWord,AveWrite):
    ########## Merging the individual path rates
#    if L1write:
#        h1 = open(output_name[:-4]+'_L1.tsv', "w")
    rateList = []
    for i in range(2*len(datasetList)+7):
        rateList.append([]) #0 Prescale
    
    rateDataset = {}
    TotalEventsPerDataset = {}
    datasetListFromFile = []
    ## fill datasetList properly
    for dataset in datasetList:
        datasetListFromFile.append(dataset)
        TotalEventsPerDataset[dataset] = 0

    
    Nlines = 0
    Nfiles = 0
    
    ### Looping over the individual .tsv files
    tmp_list = []
    test_n = 0
    for input_dir in input_dir_list:
        test_n = 0
        for tmp_file in os.listdir(input_dir):
            if not (keyWord in tmp_file) : continue
            tmp_list.append(os.path.join(input_dir,tmp_file))
            test_n += 1
            #if test_n >100: break
    test_n = 0
    for rate_file in tmp_list:
        test_n += 1
        print "*****  %d in %d processed  *****"%(test_n, len(tmp_list))
        print rate_file
        if "QCD_Pt_15to30" in rate_file:continue
        with open(rate_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            Nfiles += 1
            i = 0
            ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
            for line in tsvreader: 
                if "TotalEvents" in line[0]:
                    for k in xrange(0,len(datasetList)): 
                        #print line[k+3]
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
                        rateList[2].append(line[1])
                        rateList[3].append(line[2])
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
   
    for dataset in datasetList:
        rateDataset[dataset]=TotalEventsPerDataset[dataset]

    ### Filling up the new .tsv file with the content of the python list
    h = open(output_name, "w")
    text_rate = 'Path\tDataset\tGroup\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i]+'\t\t\t'
    text_rate += '\n'
    h.write(text_rate)

    text_rate = ""
    text_rate += "TotalEvents\t\t\t"
    for dataset in datasetList:
        text_rate += str(TotalEventsPerDataset[dataset])
        text_rate += "\t"
    text_rate = text_rate[:-1]+"\n"
    h.write(text_rate)
    for j in xrange (0,Nlines):
        if rateList[1][j] in prescaleMap:
            rateList[0][j]=prescaleMap[rateList[1][j]][0]
    for j in xrange (0,Nlines):
        tmp_ps = 1.0
        if tmp_ps < 1: tmp_ps = 1.0
        text_rate = ""
        text_rate += str(rateList[1][j])
        text_rate += "\t"
        text_rate += str(rateList[2][j])
        text_rate += "\t"
        text_rate += str(rateList[3][j])
        text_rate += "\t"

        for i in xrange(0,len(datasetList)):
            if rateList[0][j]==0 or TotalEventsPerDataset[datasetListFromFile[i]] == 0:
                rate = 0.0
                error = 0.0
            else:
                rate = rateList[2*i+6][j]*File_Factor*lumiSF/tmp_ps
                error = math.sqrt(math.fabs(rate*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]*File_Factor*lumiSF)/tmp_ps)
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
datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList
mergeRates(["../../jan19/ResultsBatch/ResultsBatch_Events/","../../jan20/ResultsBatch/ResultsBatch_Events/","../../jan21B/ResultsBatch/ResultsBatch_Events/","../../jan21C/ResultsBatch/ResultsBatch_Events/","../../jan21D/ResultsBatch/ResultsBatch_Events/","../../jan21E/ResultsBatch/ResultsBatch_Events/"],"../Results/tmp_count.tsv",'matrixEvents_',False)
#mergeRates(["../../MC_10B/ResultsBatch_v1/ResultsBatch_Events/","../../MC_10A/ResultsBatch_v1/ResultsBatch_Events/"],"../Results/output_v1.tsv",'matrixEvents_',False)


my_print(datasetList)

