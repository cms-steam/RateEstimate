# -*- coding: utf-8 -*-

import ROOT
import time
import sys
from math import *
from scipy.stats import binom
import os  
import csv

wdir = "/afs/cern.ch/user/v/vannerom/work/test/RateEstimate/ResultsBatch/"

########## Merging the individual path rates
h = open("mergedRates.tsv", "w")
rateList = []
rateList.append([]) #0 Prescale
rateList.append([]) #1 HLT path
rateList.append([]) #2 Group name
rateList.append([]) #3 Total rate
rateList.append([]) #4 Total error
rateList.append([]) #5 HLTPhysics1 rate
rateList.append([]) #6 HLTPhysics1 error
#rateList.append([]) #7 HLTPhysics2 rate
#rateList.append([]) #8 HLTPhysics2 error
#rateList.append([]) #9 HLTPhysics3 rate
#rateList.append([]) #10 HLTPhysics3 error
#rateList.append([]) #11 HLTPhysics4 rate
#rateList.append([]) #12 HLTPhysics4 error


text_rate = 'Prescale\tPath\tGroup\tTotal\t\t\t\tHLTPhysics1\t\t\t\tHLTPhysics2\t\t\t\tHLTPhysics3\t\t\t\tHLTPhysics4\t\t\t\t'
text_rate += '\n'

Nlines = 0
### Looping over the individual .tsv files
for rate_file in os.listdir("ResultsBatch"): 
    if ("L1_matrixRates" in rate_file) and not ("group" in rate_file):
        with open(wdir+rate_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            i = 0
            ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
            for line in tsvreader:
                if (line[1]!='Path') and (line[1] not in rateList[1]):
                    rateList[0].append(line[0])
                    rateList[1].append(line[1])
                    rateList[2].append(line[2])
                    rateList[3].append(float(line[3]))
                    rateList[4].append(float(line[5]))
                    rateList[5].append(float(line[6]))
                    rateList[6].append(float(line[8]))
                    #rateList[7].append(float(line[9]))
                    #rateList[8].append(float(line[11]))
                    #rateList[9].append(float(line[12]))
                    #rateList[10].append(float(line[14]))
                    #rateList[11].append(float(line[15]))
                    #rateList[12].append(float(line[17]))
                elif (line[1]!='Path'):
                    rateList[3][i] += float(line[3])
                    rateList[4][i] += float(line[5])
                    rateList[5][i] += float(line[6])
                    rateList[6][i] += float(line[8])
                    #rateList[7][i] += float(line[9])
                    #rateList[8][i] += float(line[11])
                    #rateList[9][i] += float(line[12])
                    #rateList[10][i] += float(line[14])
                    #rateList[11][i] += float(line[15])
                    #rateList[12][i] += float(line[17])
                    i += 1
            if (Nlines==0): Nlines = i

### Filling up the new .tsv file with the content of the python list
for j in xrange (0,Nlines):
    for i in xrange(0,7):
        if (i%2!=0) and (i>2):
            text_rate += str(rateList[i][j])
            text_rate += "\t+-\t"
        elif (i==6):
            text_rate += str(rateList[i][j])
            text_rate += "\n"
        else:
            text_rate += str(rateList[i][j])
            text_rate += "\t"

h.write(text_rate)
h.close()

########## Merging the group rates
f = open("mergedRates.group.tsv", "w")
groupList = []
groupList.append([]) #0 Group name
groupList.append([]) #1 Total rate
groupList.append([]) #2 Total error
groupList.append([]) #3 HLTPhysics1 rate
groupList.append([]) #4 HLTPhysics1 error
#groupList.append([]) #5 HLTPhysics2 rate
#groupList.append([]) #6 HLTPhysics2 error
#groupList.append([]) #7 HLTPhysics3 rate
#groupList.append([]) #8 HLTPhysics3 error
#groupList.append([]) #9 HLTPhysics4 rate
#groupList.append([]) #10 HLTPhysics4 error

text_group = 'Group\tTotal\t\t\t\tHLTPhysics1\t\t\t\tHLTPhysics2\t\t\t\tHLTPhysics3\t\t\t\tHLTPhysics4\t\t\t\t'
text_group += '\n'

for rate_file in os.listdir("ResultsBatch"):
    if ("matrixRates.group" in rate_file) and not ("groups.tsv" in rate_file):
        with open(wdir+rate_file) as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter="\t")
            i = 0
            for line in tsvreader:
                if (line[1]!='Path') and (line[1] not in groupList[0]):
                    groupList[0].append(line[1])
                    groupList[1].append(float(line[2]))
                    groupList[2].append(float(line[4]))
                    groupList[3].append(float(line[5]))
                    groupList[4].append(float(line[7]))
                    #groupList[5].append(float(line[8]))
                    #groupList[6].append(float(line[10]))
                    #groupList[7].append(float(line[11]))
                    #groupList[8].append(float(line[13]))
                    #groupList[9].append(float(line[14]))
                    #groupList[10].append(loat(line[16]))
                elif (line[1]!='Path'):
                    groupList[1][i] += float(line[2])
                    groupList[2][i] += float(line[4])
                    groupList[3][i] += float(line[5])
                    groupList[4][i] += float(line[7])
                    #groupList[5][i] += float(line[8])
                    #groupList[6][i] += float(line[10])
                    #groupList[7][i] += float(line[11])
                    #groupList[8][i] += float(line[13])
                    #groupList[9][i] += float(line[14])
                    #groupList[10][i] += float(line[16])
                    i += 1
            #print "i = ",i
          
for j in xrange (0,24):
    for i in xrange(0,5):
        if (i%2!=0):
            #print rateList[i][j],"  ",
            text_group += str(groupList[i][j])
            text_group += "\t+-\t"
        elif (i==4):
            #print rateList[i][j],"\n"
            text_group += str(groupList[i][j])
            text_group += "\n"
        elif (i!=0) and (i%2==0):
            #print rateList[i][j],"  ",
            text_group += str(groupList[i][j])
            text_group += "\t"
  
f.write(text_group)
f.close()
