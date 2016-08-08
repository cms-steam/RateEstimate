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
    
    text_rate = 'Prescale\tPath\tDataset\tGroup\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t'
    text_rate += '\n'
    
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
                                    rateList[ii].append(float(line[ii-2]))
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
                                    rateList[ii][i] += float(line[ii-2])
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
    
    ### Filling up the new .tsv file with the content of the python list

    for j in xrange (0,Nlines):
        if rateList[1][j] in triggersGroupMap:
            rateList[0][j]=prescaleMap[rateList[1][j]][0]
    for j in xrange (0,Nlines):
        for i in xrange(0,len(datasetList)+5):
            if i<4:
                text_rate += str(rateList[i][j])
                text_rate += "\t"
            elif i==4:
                text_rate += str(TotalRateList[j])
                text_rate += "\t"
            elif i==len(datasetList)+4:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*File_Factor
                text_rate += str(rate)
                text_rate += "\t"
            else:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*File_Factor
                text_rate += str(rate)
                text_rate += "\t"
    
    h.write(text_rate)
    h.close()

File_Factor=1.0

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mergeRates("ResultsBatch/","Results/output.tsv",'matrixEvents_ParkingZeroBias',False)


my_print(datasetList)

