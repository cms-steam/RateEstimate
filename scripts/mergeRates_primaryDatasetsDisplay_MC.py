# -*- coding: utf-8 -*-

import ROOT
import time
import sys
from math import *
from scipy.stats import binom
import os  
import csv
import math

sys.path.append('/afs/cern.ch/user/v/vannerom/work/cms-steam/RateEstimate_v5')
from triggersGroupMap.triggersGroupMap_GRun_V58_modifiable import *
from datasetCrossSections.datasetCrossSectionsSpring15 import *

wdir = "/afs/cern.ch/user/v/vannerom/work/cms-steam/RateEstimate_v5/ResultsBatch/"

########## Merging the individual path rates
h = open("mergedRates_MC.tsv", "w")
rateList = []
rateList.append([]) #0 Prescale
rateList.append([]) #1 HLT path
rateList.append([]) #2 Group
rateList.append([]) #3 Primary dataset
rateList.append([]) #4 Total rate
rateList.append([]) #5 QCDPt15to30 rate
rateList.append([]) #6 QCDPt30to50 rate
rateList.append([]) #7 QCDPt50to80 rate
rateList.append([]) #8 QCDPt80to120 rate
rateList.append([]) #9 QCDPt120to170 rate
rateList.append([]) #10 QCDPt170to300 rate
rateList.append([]) #11 QCDPt300to470 rate
rateList.append([]) #12 QCDPt470to600 rate
rateList.append([]) #13 DYToLLM1 rate
rateList.append([]) #14 WJetsToLNu rate
rateList.append([]) #15 QCDPt15to20EMEnriched rate
rateList.append([]) #16 QCDPt20to30EMEnriched rate
rateList.append([]) #17 QCDPt30to50EMEnriched rate
rateList.append([]) #18 QCDPt50to80EMEnriched rate
rateList.append([]) #19 QCDPt80to120EMEnriched rate
rateList.append([]) #20 QCDPt120to170EMEnriched rate
rateList.append([]) #21 QCDPt15to20MuEnrichedPt5 rate
rateList.append([]) #22 QCDPt20to30MuEnrichedPt5 rate
rateList.append([]) #23 QCDPt30to50MuEnrichedPt5 rate
rateList.append([]) #24 QCDPt50to80MuEnrichedPt5 rate
rateList.append([]) #25 QCDPt80to120MuEnrichedPt5 rate
rateList.append([]) #26 QCDPt120to170MuEnrichedPt5 rate

text_rate = 'Prescale\tPath\tGroup\tDataset\tTotal\t\t\t\tQCDPt15to30\t\t\tQCDPt30to50\t\t\tQCDPt50to80\t\t\tQCDPt80to120\t\t\tQCDPt120to170\t\t\tQCDPt170to300\t\t\tQCDPt300to470\t\t\tQCDPt470to600\t\t\tDYToLLM1\t\t\tWJetsToLNu\t\t\tQCDPt15to20EMEnriched\t\t\tQCDPt20to30EMEnriched\t\t\tQCDPt30to50EMEnriched\t\t\tQCDPt50to80EMEnriched\t\t\tQCDPt80to120EMEnriched\t\t\tQCDPt120to170EMEnriched\t\t\tQCDPt15to20MuEnrichedPt5\t\t\tQCDPt20to30MuEnrichedPt5\t\t\tQCDPt30to50MuEnrichedPt5\t\t\tQCDPt50to80MuEnrichedPt5\t\t\tQCDPt80to120MuEnrichedPt5\t\t\tQCDPt120to170MuEnrichedPt5\t\t\t'
text_rate += '\n'

lumi = 2E33
rateDataset = {}
TotalEventsPerDataset = {}
datasetListFromFile = []
## fill datasetList properly
datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList
for dataset in datasetList:
    rateDataset [dataset] = lumi*xsectionDatasets[dataset]*1E-24/1E12 # [1b = 1E-24 cm^2, 1b = 1E12pb ]
    datasetListFromFile.append(dataset)
    TotalEventsPerDataset[dataset] = 0

Nlines = 0
Nfiles = 0

### Looping over the individual .tsv files
for rate_file in os.listdir(wdir):
    #print rate_file
    if ("matrixEvents" in rate_file) and not ("group" in rate_file) and not ("primaryDataset" in rate_file):
        with open(wdir+rate_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            Nfiles += 1
            i = 0
            ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
            for line in tsvreader: 
		if "TotalEvents" in line[0]:
   			for k in xrange(0,22): TotalEventsPerDataset[datasetListFromFile[k]] += float(line[k+3])
                groupCheck = False
                if (line[0]!='Path') and (line[0] not in rateList[1]):
                    for group in groupList: 
                        if group in line[1]: groupCheck = True
                    if (groupCheck or ("TotalEvents" in line[0])): 
                        rateList[0].append(1) # Need to be changed to prescales
                    	rateList[1].append(line[0])
                    	rateList[2].append(line[1])
                        rateList[3].append(line[2])
                        rateList[5].append(rateDataset[datasetListFromFile[0]]*float(line[3]))
                        rateList[6].append(rateDataset[datasetListFromFile[1]]*float(line[4]))
                        rateList[7].append(rateDataset[datasetListFromFile[2]]*float(line[5]))
                        rateList[8].append(rateDataset[datasetListFromFile[3]]*float(line[6]))
                        rateList[9].append(rateDataset[datasetListFromFile[4]]*float(line[7]))
                        rateList[10].append(rateDataset[datasetListFromFile[5]]*float(line[8]))
                        rateList[11].append(rateDataset[datasetListFromFile[6]]*float(line[9]))
                        rateList[12].append(rateDataset[datasetListFromFile[7]]*float(line[10]))
                        rateList[13].append(rateDataset[datasetListFromFile[8]]*float(line[11]))
                        rateList[14].append(rateDataset[datasetListFromFile[9]]*float(line[12]))
                        rateList[15].append(rateDataset[datasetListFromFile[10]]*float(line[13]))
                        rateList[16].append(rateDataset[datasetListFromFile[11]]*float(line[14]))
                        rateList[17].append(rateDataset[datasetListFromFile[12]]*float(line[15]))
                        rateList[18].append(rateDataset[datasetListFromFile[13]]*float(line[16]))
                        rateList[19].append(rateDataset[datasetListFromFile[14]]*float(line[17]))
                        rateList[20].append(rateDataset[datasetListFromFile[15]]*float(line[18]))
                        rateList[21].append(rateDataset[datasetListFromFile[16]]*float(line[19]))
                        rateList[22].append(rateDataset[datasetListFromFile[17]]*float(line[20]))
                        rateList[23].append(rateDataset[datasetListFromFile[18]]*float(line[21]))
                        rateList[24].append(rateDataset[datasetListFromFile[19]]*float(line[22]))
                        rateList[25].append(rateDataset[datasetListFromFile[20]]*float(line[23]))
                        rateList[26].append(rateDataset[datasetListFromFile[21]]*float(line[24]))
                        #rateList[3].append(rateDataset[datasetListFromFile[0]]*float(line[2])+rateDataset[datasetListFromFile[1]]*float(line[3])+rateDataset[datasetListFromFile[2]]*float(line[4])+rateDataset[datasetListFromFile[3]]*float(line[5])+rateDataset[datasetListFromFile[4]]*float(line[6])+rateDataset[datasetListFromFile[5]]*float(line[7])+rateDataset[datasetListFromFile[6]]*float(line[8])+rateDataset[datasetListFromFile[7]]*float(line[9])+rateDataset[datasetListFromFile[8]]*float(line[10])+rateDataset[datasetListFromFile[9]]*float(line[11])+rateDataset[datasetListFromFile[10]]*float(line[12])+rateDataset[datasetListFromFile[11]]*float(line[13])+rateDataset[datasetListFromFile[12]]*float(line[14])+rateDataset[datasetListFromFile[13]]*float(line[15])+rateDataset[datasetListFromFile[14]]*float(line[16])+rateDataset[datasetListFromFile[15]]*float(line[17])+rateDataset[datasetListFromFile[16]]*float(line[18])+rateDataset[datasetListFromFile[17]]*float(line[19])+rateDataset[datasetListFromFile[18]]*float(line[20])+rateDataset[datasetListFromFile[19]]*float(line[21])+rateDataset[datasetListFromFile[20]]*float(line[22])+rateDataset[datasetListFromFile[21]]*float(line[23]))
                elif (line[0]!='Path'):
                    for group in groupList:
                        if group in line[1]: groupCheck = True
                    if (groupCheck or ("TotalEvents" in line[0])):
                        rateList[5][i] += rateDataset[datasetListFromFile[0]]*float(line[3])
                        rateList[6][i] += rateDataset[datasetListFromFile[1]]*float(line[4])
                        rateList[7][i] += rateDataset[datasetListFromFile[2]]*float(line[5])
                        rateList[8][i] += rateDataset[datasetListFromFile[3]]*float(line[6])
                        rateList[9][i] += rateDataset[datasetListFromFile[4]]*float(line[7])
                        rateList[10][i] += rateDataset[datasetListFromFile[5]]*float(line[8])
                        rateList[11][i] += rateDataset[datasetListFromFile[6]]*float(line[9])
                        rateList[12][i] += rateDataset[datasetListFromFile[7]]*float(line[10])
                        rateList[13][i] += rateDataset[datasetListFromFile[8]]*float(line[11])
                        rateList[14][i] += rateDataset[datasetListFromFile[9]]*float(line[12])
                        rateList[15][i] += rateDataset[datasetListFromFile[10]]*float(line[13])
                        rateList[16][i] += rateDataset[datasetListFromFile[11]]*float(line[14])
                        rateList[17][i] += rateDataset[datasetListFromFile[12]]*float(line[15])
                        rateList[18][i] += rateDataset[datasetListFromFile[13]]*float(line[16])
                        rateList[19][i] += rateDataset[datasetListFromFile[14]]*float(line[17])
                        rateList[20][i] += rateDataset[datasetListFromFile[15]]*float(line[18])
                        rateList[21][i] += rateDataset[datasetListFromFile[16]]*float(line[19])
                        rateList[22][i] += rateDataset[datasetListFromFile[17]]*float(line[20])
                        rateList[23][i] += rateDataset[datasetListFromFile[18]]*float(line[21])
                        rateList[24][i] += rateDataset[datasetListFromFile[19]]*float(line[22])
                        rateList[25][i] += rateDataset[datasetListFromFile[20]]*float(line[23])
                        rateList[26][i] += rateDataset[datasetListFromFile[21]]*float(line[24])
                        #for j in xrange (4,26):
                        #    rateList[3][i] += rateList[j][i]
                        i += 1
            if (Nlines==0): Nlines = i

print "Nfiles = ",Nfiles

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

def sqrtMod(x):
    if x>0: return sqrt(x)
    else: return 0

TotalRateList = []
TotalErrorList = []

for j in xrange (0,Nlines):
    TotalRateList.append(0)
    TotalErrorList.append(0)
    for i in xrange(5,27):
        denominator = TotalEventsPerDataset[datasetListFromFile[i-5]] 
        if denominator==0: denominator = 1
        TotalRateList[j] += rateList[i][j]/denominator
        TotalErrorList[j] += ((rateDataset[datasetListFromFile[i-5]]*rateList[i][j])/(denominator*denominator))
print "Nlines = ",Nlines
### Filling up the new .tsv file with the content of the python list
for j in xrange (0,Nlines):
    print j
    for i in xrange(0,27):
        if i<4:
            text_rate += str(rateList[i][j])
            text_rate += "\t"
        elif i==4:
            text_rate += str(TotalRateList[j])
            text_rate += "\t±\t"
            text_rate += str(sqrtMod(TotalErrorList[j]))
            text_rate += "\t"
        elif i==26:
            if rateList[i][0]==0:
                rate = 0
                error = 0
            else:
                rate = rateList[i][j]/TotalEventsPerDataset[datasetListFromFile[i-5]]
                error = sqrtMod((rateDataset[datasetListFromFile[i-5]]*rate)/TotalEventsPerDataset[datasetListFromFile[i-5]])
            text_rate += str(rate)
            text_rate += "\t±\t"
            text_rate += str(error)
            text_rate += "\n"
        else:
            if rateList[i][0]==0:
                rate = 0
                error = 0
            else:
                rate = rateList[i][j]/TotalEventsPerDataset[datasetListFromFile[i-5]]
                error = sqrtMod((rateDataset[datasetListFromFile[i-5]]*rate)/TotalEventsPerDataset[datasetListFromFile[i-5]])
            text_rate += str(rate)
            text_rate += "\t±\t"
            text_rate += str(error)
            text_rate += "\t"

h.write(text_rate)
h.close()
