# -*- coding: utf-8 -*-
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *
from triggersGroupMap.Menu_online_v3p1_V4_Evaluate_Rates import *
from myref1 import *
#import ROOT
import time
import sys
#from math import *
#from scipy.stats import binom
import os  
import csv
import math

ps_const = 11245.0*2200.0
psNorm = {
'ParkingZeroBias0':2323622,
'ParkingZeroBias1':2295892,
'ParkingZeroBias2':2289945,
'ParkingZeroBias3':2258518,
'ParkingZeroBias4':2319876,
}
for dataset in datasetList:
    xsection = xsectionDatasets[dataset]


def my_print(datasetList):
    for dataset in datasetList:
        print dataset
    print len(datasetList)

def mergeRates(input_dir,output_name,keyWord,L1write):
    wdir = input_dir
    
    ########## Merging the individual path rates
    h = open(output_name, "w")
    if L1write:
        h1 = open(output_name[:-4]+'_L1.tsv', "w")
    rateList = []
    for i in range(len(datasetList)+5):
        rateList.append([]) #0 Prescale
    
    #text_rate = 'Prescale\tPath\tGroup\tTotal\t\t\t\tHLTPhysics1\t\t\t\tHLTPhysics2\t\t\t\tHLTPhysics3\t\t\t\tHLTPhysics4\t\t\t\t'
    #text_rate = 'Prescale\tPath\tGroup\tTotal\t\t\t\tQCDPt15to30\t\t\tQCDPt30to50\t\t\tQCDPt50to80\t\t\tQCDPt80to120\t\t\tQCDPt120to170\t\t\tQCDPt170to300\t\t\tQCDPt300to470\t\t\tQCDPt470to600\t\t\tDYToLLM1\t\t\tWJetsToLNu\t\t\tQCDPt15to20EMEnriched\t\t\tQCDPt20to30EMEnriched\t\t\tQCDPt30to50EMEnriched\t\t\tQCDPt50to80EMEnriched\t\t\tQCDPt80to120EMEnriched\t\t\tQCDPt120to170EMEnriched\t\t\tQCDPt15to20MuEnrichedPt5\t\t\tQCDPt20to30MuEnrichedPt5\t\t\tQCDPt30to50MuEnrichedPt5\t\t\tQCDPt50to80MuEnrichedPt5\t\t\tQCDPt80to120MuEnrichedPt5\t\t\tQCDPt120to170MuEnrichedPt5\t\t\t'
    text_rate = 'Prescale\tPath\tDataset\tGroup\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
    text_rate += '\n'
    
    if L1write:
        text_rate1 = 'Prescale\tPath\tGroup\tL1 seed\tL1 prescale\t\ttotal\t\t\t'
        for i in range(len(datasetList)):
            text_rate1+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
        text_rate1 += '\n'
    
    rateDataset = {}
    TotalEventsPerDataset = {}
    datasetListFromFile = []
    total_ps = 0
    ## fill datasetList properly
    for dataset in datasetList:
        #rateDataset [dataset] = (1./psNorm[dataset])*lenLS*nLS[dataset]*xsection# [1b = 1E-24 cm^2, 1b = 1E12pb ]
        rateDataset [dataset] = (ps_const/psNorm[dataset])# [1b = 1E-24 cm^2, 1b = 1E12pb ]
        total_ps += psNorm[dataset]
        print rateDataset [dataset]
        datasetListFromFile.append(dataset)
        TotalEventsPerDataset[dataset] = 0
    total_ps = ps_const/total_ps

    
    Nlines = 0
    Nfiles = 0
    
    ### Looping over the individual .tsv files
    for rate_file in os.listdir(wdir):
        #print rate_file
        if (keyWord in rate_file) and not ("group" in rate_file):
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
                    groupCheck = True
                    if (line[0]!='Path') and (line[0] not in rateList[1]):
                        if (groupCheck ): 
                            rateList[0].append(-1) # Need to be changed to prescales
                            rateList[1].append(line[0])
                            rateList[3].append(line[1])
                            rateList[2].append(line[2])
                            for ii in range(5,len(datasetList)+5):
                                if "TotalEvents" in line[0]:
                                    rateList[ii].append(float(line[ii-2]))
                                else:
                                    rateList[ii].append(float(line[ii-2])*lumiSF)
                            tmp_rate=0.0
                            for ii in range(5,len(datasetList)+5):
                                tmp_rate+=rateList[ii][i]
                            rateList[4].append(tmp_rate)
                            #for j in xrange (4,26):
                                #print "i = ",i,", j = ",j
                            #    rateList[3][0] += rateList[j][0]
                            #print rate_file," ",rateList[3][0]
                            i += 1
                    elif (line[0]!='Path'):
                        if (groupCheck ):
                            #print rate_file
                            for ii in range(5,len(datasetList)+5):
                                if "TotalEvents" in line[0]:
                                    rateList[ii][i] += float(line[ii-2])
                                else:
                                    rateList[ii][i] += float(line[ii-2])*lumiSF
                            for j in xrange (5,len(datasetList)+5):
                                #print "i = ",i,", j = ",j
                                rateList[4][i] += rateList[j][i]
                            #print i," ",rate_file," ",rateList[3][i]
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
    
    
    for j in xrange (0,Nlines):
        TotalRateList.append(0)
        TotalErrorList.append(0)
        for i in xrange(5,len(datasetList)+5):
                TotalRateList[j] += File_Factor*rateList[i][j]
        if 'TotalEvents' in rateList[1][j]:continue
        TotalRateList[j] *= total_ps
        TotalErrorList[j] = math.sqrt(math.fabs(float(TotalRateList[j])*total_ps))
    
    ### Filling up the new .tsv file with the content of the python list

    for j in xrange (0,Nlines):
        if rateList[1][j] in triggersGroupMap:
            rateList[0][j]=prescaleMap[rateList[1][j]][0]
    for j in xrange (0,Nlines):
        tmp_ps = 0
        tmp_ps = float(int(rateList[0][j]))
        if tmp_ps <1:
            tmp_ps = 1
        if not UnprescaledCount:
            tmp_ps = 1
        for i in xrange(0,len(datasetList)+5):
            if i<4:
                text_rate += str(rateList[i][j])
                text_rate += "\t"
            elif i==4:
                text_rate += str(TotalRateList[j]/tmp_ps)
                text_rate += "\t+/-\t"
                text_rate += str(TotalErrorList[j]/tmp_ps)
                text_rate += "\t"
            elif i==len(datasetList)+4:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*rateDataset[datasetListFromFile[i-5]]*File_Factor
                    error = math.sqrt(math.fabs(rate*rateDataset[datasetListFromFile[i-5]]))
                text_rate += str(rate/tmp_ps)
                text_rate += "\t+/-\t"
                text_rate += str(error/tmp_ps)
                text_rate += "\n"
            else:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*rateDataset[datasetListFromFile[i-5]]*File_Factor
                    error = math.sqrt(math.fabs(rate*rateDataset[datasetListFromFile[i-5]]))
                text_rate += str(rate/tmp_ps)
                text_rate += "\t+/-\t"
                text_rate += str(error/tmp_ps)
                text_rate += "\t"
    
    h.write(text_rate)
    h.close()

File_Factor=1.0
lumiSF=1.
UnprescaledCount = True

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mergeRates("ResultsBatch/","Results/output.tsv",'matrixEvents_ParkingZeroBias',False)


my_print(datasetList)

