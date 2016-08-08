# -*- coding: utf-8 -*-
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *
from myref1 import *
#import ROOT
import time
import sys
#from math import *
#from scipy.stats import binom
import os  
import csv
import math

lenLS = 23.31 ## length of Lumi Section
nLS =2740 ## number of Lumi Sections run over data
psNorm = 12. * 15013. / 4. # Prescale Normalization factor if running on HLTPhysics
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
    text_rate = 'path\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t'
    text_rate += '\n'
    
    if L1write:
        text_rate1 = 'Prescale\tPath\tGroup\tL1 seed\tL1 prescale\t\ttotal\t\t\t'
        for i in range(len(datasetList)):
            text_rate1+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
        text_rate1 += '\n'
    
    rateDataset = {}
    TotalEventsPerDataset = {}
    datasetListFromFile = []
    ## fill datasetList properly
    for dataset in datasetList:
        rateDataset [dataset] = 1#(1./psNorm)*lenLS*nLS*xsection# [1b = 1E-24 cm^2, 1b = 1E12pb ]
        print rateDataset [dataset]
        datasetListFromFile.append(dataset)
        TotalEventsPerDataset[dataset] = 0

#    return
    
    Nlines = 0
    Nfiles = 0
    
    ### Looping over the individual .tsv files
    for rate_file in os.listdir(wdir):
        #print rate_file
        if (keyWord in rate_file) :
#        if ("pu23to27rates_MC_v4p4_V1__frozen_2015_25ns14e33_v4p4_HLT_V1_2e33_PUfilterGen_matrixEvents.tsv" in rate_file) and not ("group" in rate_file):
            with open(wdir+rate_file) as tsvfile:
                tsvreader = csv.reader(tsvfile, delimiter="\t")
                Nfiles += 1
                i = 0
                ### For each .tsv file, looping over the lines of the text file and filling the python list with the summed rates
                for line in tsvreader: 
    		    if "TotalEvents" in line[0]:
       			for k in xrange(0,len(datasetList)): 
                            TotalEventsPerDataset[datasetListFromFile[k]] += float(line[k+1])
                        print TotalEventsPerDataset
                        print line
                        print "*"*30
                        print len(line)
                        print "*"*30
                    groupCheck = True
                    #print "line[0]: ",line[0],", ","line[1]: ",line[1],", ","line[2]: ",line[2],", ","line[3]: ",line[3],", ","line[4]: ",line[4],"line[5]: ",line[5],", ","line[6]: ",line[6],"line[7]: ",line[7],", ","line[8]: ",line[8]#,", ","line[9]: ",line[9],", ","line[10]: ",line[10],", ","line[11]: ",line[11],"line[12]: ",line[12],", ","line[13]: ",line[13],"line[14]: ",line[14],", ","line[15]: ",line[15],", ","line[16]: ",line[16],", ","line[17]: ",line[17],", ","line[18]: ",line[18],"line[19]: ",line[19],", ","line[20]: ",line[20],"line[21]: ",line[21],", ","line[22]: ",line[22],", ","line[23]: ",line[23],", ","line[24]: ",line[24],", ","line[25]: ",line[25],"line[26]: ",line[26],", ","line[27]: ",line[27],"line[28]: ",line[28],"line[29]: ",line[29],", ","line[30]: ",line[30]
                    if (line[0]!='Path') and (line[0] not in rateList[0]):
                        if (groupCheck ): 
                            rateList[0].append(line[0])
                            for ii in range(2,len(datasetList)+2):
                                if "TotalEvents" in line[0]:
                                    rateList[ii].append(float(line[ii-1]))
                                else:
                                    rateList[ii].append(float(line[ii-1])/rateDataset[datasetListFromFile[ii-2]]*lumiSF)
                            tmp_rate=0.0
                            for ii in range(2,len(datasetList)+2):
                                tmp_rate+=rateList[ii][i]
                            rateList[1].append(tmp_rate)
                            i += 1
                    elif (line[0]!='Path'):
                        if (groupCheck ):
                            #print rate_file
                            for ii in range(2,len(datasetList)+2):
                                if "TotalEvents" in line[0]:
                                    rateList[ii][i] += float(line[ii-1])
                                else:
                                    rateList[ii][i] += float(line[ii-1])/rateDataset[datasetListFromFile[ii-2]]*lumiSF
                            for j in xrange (2,len(datasetList)+2):
                                #print "i = ",i,", j = ",j
                                rateList[1][i] += rateList[j][i]
                            #print i," ",rate_file," ",rateList[3][i]
                            i += 1
                print rateList[0][1],rateList[1][1]
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
        for i in xrange(2,len(datasetList)+2):
                TotalRateList[j] += File_Factor*rateList[i][j]
                TotalErrorList[j] += (File_Factor*rateList[i][j]/rateDataset[datasetListFromFile[i-2]])
        TotalErrorList[j] = math.sqrt(math.fabs(float(TotalErrorList[j])))
    
    ### Filling up the new .tsv file with the content of the python list

    for j in xrange (0,Nlines):
        for i in xrange(0,len(datasetList)+2):
            #print i," ",rateList[i][0]
            if i<1:
                text_rate += str(rateList[i][j])
                text_rate += "\t"
            elif i==1:
                #total rate
                text_rate += str(TotalRateList[j])
                text_rate += "\t"
            elif i==len(datasetList)+1:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*File_Factor
                    error = math.sqrt(math.fabs(rate/rateDataset[datasetListFromFile[i-2]]))
                text_rate += str(rate)
                text_rate += "\n"
            else:
                if rateList[i][0]==0:
                    rate = 0
                    error = 0
                else:
                    rate = rateList[i][j]*File_Factor
                    error = math.sqrt(math.fabs(rate/rateDataset[datasetListFromFile[i-2]]))
                text_rate += str(rate)
                text_rate += "\t"
    
    h.write(text_rate)
    h.close()


def downloadmenu(linkToGoogleDOC):
    nameMenu = "_frozen_2015_25ns14e33_v4.4_HLT_V2"
    try:    
        os.mkdir('tmp')
    except:
        pass
    ### Download the googleDOC in .tsv format ###
    if "edit#gid=0" in linkToGoogleDOC:
        linkToGoogleDOC = linkToGoogleDOC[:-10]

    linkToGoogleDOCsplitted=linkToGoogleDOC.split("/")
    code = linkToGoogleDOCsplitted[len(linkToGoogleDOCsplitted)-2]
    linkToGoogleDOCtsv = linkToGoogleDOC + "export?format=tsv&id=" + code + "&gid=0"
    command = 'wget -O tmp/'+nameMenu+".tsv "+linkToGoogleDOCtsv
    filename = 'tmp/'+nameMenu+'.tsv'
    print command
    os.popen(command,'r').read()
    return filename

menu_lumibiasdic={
'1e33':3,
'2e33':2,
'5e33':0,
'7e33':-1,
'1e34':-2
}

index_lumi='1e34'
file3_hltpath = 2           #HLT_
file3_hltprescale = 22+int(menu_lumibiasdic[index_lumi])      #l1 prescale
file3_l1path = 6           #L1_
file3_l1prescale = 10+int(menu_lumibiasdic[index_lumi])      #l1 prescale

file4_l1path = 1           #L1_
#file4_l1prescale = 5+int(menu_lumibiasdic[index_lumi])      #l1 prescale
file4_l1prescale = 0     #l1 prescale

File_Factor=1.0
#lumiSF = 10. /7.24
lumiSF = 1

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Menuname=downloadmenu('https://docs.google.com/spreadsheets/d/1Xka2ltnQ0-aT-r62M54ThY_2Bdxj6QDk5gCb0kVsrB0/edit#gid=0')

mergeRates("ResultsBatch/","Results/outputCount.group.tsv",'matrixEvents.groups',False)
mergeRates("ResultsBatch/","Results/outputCount.dataset.tsv",'matrixEvents.primaryDataset',False)
#mergeRates("ResultsBatch_first/","Results/output.group.tsv",'matrixEvents.groups_HLTPhysics',False)



my_print(datasetList)

