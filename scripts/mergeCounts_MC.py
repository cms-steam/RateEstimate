# -*- coding: utf-8 -*-
from triggersGroupMap.triggersGroupMap__frozen_2015_25ns14e33_v4p4_HLT_V1 import *
import ROOT
import time
import sys
from math import *
from scipy.stats import binom
import os  
import csv
import math

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

wdir = "/afs/cern.ch/user/v/vannerom/work/cms-steam/RateEstimate/ResultsBatch_1e34_PU23to27/"

########## Merging the individual path rates
h = open("mergedCounts_MC.tsv", "w")
rateList = []
rateList.append([]) #0 HLT path
rateList.append([]) #1 Group name
rateList.append([]) #2 QCDPt15to30 count
rateList.append([]) #3 QCDPt30to50 count
rateList.append([]) #4 QCDPt50to80 count
rateList.append([]) #5 QCDPt80to120 count
rateList.append([]) #6 QCDPt120to170 count
rateList.append([]) #7 QCDPt170to300 count
rateList.append([]) #8 QCDPt300to470 count
rateList.append([]) #9 QCDPt470to600 count
rateList.append([]) #10 DYToLLM1 count
rateList.append([]) #11 WJetsToLNu count
rateList.append([]) #12 QCDPt15to20EMEnriched count
rateList.append([]) #13 QCDPt20to30EMEnriched count
rateList.append([]) #14 QCDPt30to50EMEnriched count
rateList.append([]) #15 QCDPt50to80EMEnriched count
rateList.append([]) #16 QCDPt80to120EMEnriched count
rateList.append([]) #17 QCDPt120to170EMEnriched count
rateList.append([]) #18 QCDPt15to20MuEnrichedPt5 count
rateList.append([]) #19 QCDPt20to30MuEnrichedPt5 count
rateList.append([]) #20 QCDPt30to50MuEnrichedPt5 count
rateList.append([]) #21 QCDPt50to80MuEnrichedPt5 count
rateList.append([]) #22 QCDPt80to120MuEnrichedPt5 count
rateList.append([]) #23 QCDPt120to170MuEnrichedPt5 count

#text_rate = 'Prescale\tPath\tGroup\tTotal\t\t\t\tHLTPhysics1\t\t\t\tHLTPhysics2\t\t\t\tHLTPhysics3\t\t\t\tHLTPhysics4\t\t\t\t'
text_rate = 'Path\tGroup\tQCDPt15to30\tQCDPt30to50\tQCDPt50to80\tQCDPt80to120\tQCDPt120to170\tQCDPt170to300\tQCDPt300to470\tQCDPt470to600\tDYToLLM1\tWJetsToLNu\tQCDPt15to20EMEnriched\tQCDPt20to30EMEnriched\tQCDPt30to50EMEnriched\tQCDPt50to80EMEnriched\tQCDPt80to120EMEnriched\tQCDPt120to170EMEnriched\tQCDPt15to20MuEnrichedPt5\tQCDPt20to30MuEnrichedPt5\tQCDPt30to50MuEnrichedPt5\tQCDPt50to80MuEnrichedPt5\tQCDPt80to120MuEnrichedPt5\tQCDPt120to170MuEnrichedPt5\t'
text_rate += '\n'

Nlines = 0
Nfiles = 0
### Looping over the individual .tsv files
for rate_file in os.listdir(wdir):
    if ("matrixEvents" in rate_file) and not ("group" in rate_file):
        with open(wdir+rate_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            Nfiles += 1
            i = 0
            ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
            for line in tsvreader:
                groupCheck = False  
                if (line[0]!='Path') and (line[0] not in rateList[0]):
                    for group in groupList: 
                        if group in line[1]: groupCheck = True
                    if (groupCheck or ("TotalEvents" in line[0])): 
                        rateList[0].append(line[0])
                        rateList[1].append(line[1])
                        rateList[2].append(float(line[2]))
                        rateList[3].append(float(line[3]))
                        rateList[4].append(float(line[4]))
                        rateList[5].append(float(line[5]))
                        rateList[6].append(float(line[6]))
                        rateList[7].append(float(line[7]))
                        rateList[8].append(float(line[8]))
                        rateList[9].append(float(line[9])) 
                        rateList[10].append(float(line[10]))
                        rateList[11].append(float(line[11])) 
                        rateList[12].append(float(line[12]))
                        rateList[13].append(float(line[13]))
                        rateList[14].append(float(line[14]))
                        rateList[15].append(float(line[15]))
                        rateList[16].append(float(line[16]))
                        rateList[17].append(float(line[17]))
                        rateList[18].append(float(line[18]))
                        rateList[19].append(float(line[19]))
                        rateList[20].append(float(line[20]))
                        rateList[21].append(float(line[21]))
                        rateList[22].append(float(line[22]))
                        rateList[23].append(float(line[23])) 
                elif (line[0]!='Path'):
                    for group in groupList:
                        if group in line[1]: groupCheck = True
                    if (groupCheck or ("TotalEvents" in line[0])): 
                        rateList[2][i] += float(line[2])
                        rateList[3][i] += float(line[3])
                        rateList[4][i] += float(line[4])
                        rateList[5][i] += float(line[5])
                        rateList[6][i] += float(line[6])
                        rateList[7][i] += float(line[7])
                        rateList[8][i] += float(line[8])
                        rateList[9][i] += float(line[9])
                        rateList[10][i] += float(line[10]) 
                        rateList[11][i] += float(line[11]) 
                        rateList[12][i] += float(line[12])
                        rateList[13][i] += float(line[13])
                        rateList[14][i] += float(line[14])
                        rateList[15][i] += float(line[15])
                        rateList[16][i] += float(line[16])
                        rateList[17][i] += float(line[17])
                        rateList[18][i] += float(line[18])
                        rateList[19][i] += float(line[19])
                        rateList[20][i] += float(line[20])
                        rateList[21][i] += float(line[21])
                        rateList[22][i] += float(line[22])
                        rateList[23][i] += float(line[23])
                        i += 1
            if (Nlines==0): Nlines = i

print "Nfiles = ",Nfiles

### Filling up the new .tsv file with the content of the python list
for j in xrange (0,Nlines):
    if (("DiPFJetAve40_v2" in rateList[0][j]) and rateList[11][j]<0): print rateList[11][j]
    for i in xrange(0,24):
        if (i==23):
            text_rate += str(rateList[i][j])
            text_rate += "\n"
        else:
            text_rate += str(rateList[i][j])
            text_rate += "\t"

h.write(text_rate)
h.close()
