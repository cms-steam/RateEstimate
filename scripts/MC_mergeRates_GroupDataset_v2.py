# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../")
import os  
import csv
import math
from datasetCrossSections.datasetCrossSections_MC_test import *
from triggersGroupMap.Menu_online_v3p1_V4 import *

Method = 0 #0: rate = count ; 11: MC rate
lumi = 1.15E34
for dataset in datasetList:
    xsection = xsectionDatasets[dataset]

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

def my_print(datasetList):
    for dataset in datasetList:
        print dataset
    print len(datasetList)

def ReadRates(input_dir,keyWord):
    wdir = input_dir
    
    ########## Merging the individual path rates
#    if L1write:
#        h1 = open(output_name[:-4]+'_L1.tsv', "w")
    rateList = []
    for i in range(2*len(datasetList)+5):
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
                            print line[k+1]
                            TotalEventsPerDataset[datasetListFromFile[k]] += float(line[k+1])
                        print TotalEventsPerDataset
                        print line
                        print "*"*30
                        print len(line)
                        print "*"*30
                        continue
                    groupCheck = True
                    if (line[0]!='Path') and (line[0] not in rateList[0]):
                        if (groupCheck ): 
                            rateList[0].append(line[0])
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+3].append(float(line[3*ii+1]))
                                rateList[2*ii+4].append(float(line[3*ii+3])**2)
                            tmp_count=0.0
                            tmp_error_sq=0.0
                            i += 1
                    elif (line[0]!='Path'):
                        if (groupCheck ):
                            for ii in range(0,len(datasetList)):
                                rateList[2*ii+3][i] += float(line[3*ii+1])
                                rateList[2*ii+4][i] += float(line[3*ii+3])**2
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
   
    if Method==0:
        for dataset in datasetList:
            rateDataset[dataset]=TotalEventsPerDataset[dataset]

    elif Method==11:
        for dataset in datasetList:
            print "lumi = ",lumi," xsection = ",xsection
            rateDataset [dataset] = lumi*xsection*1E-24/1E12 # [1b = 1E-24 cm^2, 1b = 1E12pb ]
    else:
        for dataset in datasetList:
            rateDataset[dataset]=0
    rateDataset_total = 0

    
    for j in xrange (0,Nlines):
        TotalRateList.append(0)
        TotalErrorList.append(0)
        for i in xrange(0,len(datasetList)):
                TotalRateList[j] += rateList[2*i+3][j]*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]
                TotalErrorList[j] += rateList[2*i+3][j]*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]
        TotalErrorList[j] = math.sqrt(math.fabs(TotalErrorList[j]))
    
    return Nlines,rateList,TotalRateList,TotalErrorList,rateDataset,rateDataset_total,TotalEventsPerDataset,datasetListFromFile

def WriteRates(input_dir,output_dir,output_name,keyWord,type_in='',elementlist=[],Plot=False):
    (Nlines,rateList,TotalRateList,TotalErrorList,rateDataset,rateDataset_total,TotalEventsPerDataset,datasetListFromFile)=ReadRates(input_dir,keyWord)
    ### Filling up the new .tsv file with the content of the python list
    h = open(output_dir+'/'+output_name, "w")
    text_rate = 'Path\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
    text_rate += '\n'

    text_rate += "TotalEvents\t\t\t\t"
    for dataset in datasetList:
        text_rate += str(TotalEventsPerDataset[dataset])
        text_rate += "\t\t\t"
    text_rate = text_rate[:-1]+"\n"
    h.write(text_rate)
    for j in xrange (0,Nlines):
        text_rate = ""
        text_rate += str(rateList[0][j])
        text_rate += "\t"

        text_rate += str(TotalRateList[j]*File_Factor*lumiSF)
        text_rate += "\t+/-\t"
        text_rate += str(TotalErrorList[j]*File_Factor*lumiSF)
        text_rate += "\t"
        for i in xrange(0,len(datasetList)):
            #if rateList[2*i+3][0]==0:
            #    rate = 0
            #    error = 0
            #else:
            rate = rateList[2*i+3][j]*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]*File_Factor*lumiSF
            error = math.sqrt(math.fabs(rate*rateDataset[datasetListFromFile[i]]/TotalEventsPerDataset[datasetListFromFile[i]]*File_Factor*lumiSF))
            text_rate += str(rate)
            text_rate += "\t+/-\t"
            text_rate += str(error)
            text_rate += "\t"
    
        text_rate = text_rate[:-1]+"\n"
        h.write(text_rate)
    h.close()
    if Plot:
        import ROOT
        for elem_1 in elementlist:
            k=rateList[0].index(str(elem_1))

def WriteRates_2(input_dir,output_dir,output_name,keyWord,type_in='',elementlist=[],Plot=False):
    (Nlines,rateList,TotalRateList,TotalErrorList,rateDataset,rateDataset_total,TotalEventsPerDataset,datasetListFromFile)=ReadRates(input_dir,keyWord)
    ### Filling up the new .tsv file with the content of the python list
    h = open(output_dir+'/'+output_name, "w")
    text_rate = 'Path\t\tTotal\t\t\t'
    for i in range(len(datasetList)):
        text_rate+=datasetList[i].split('_TuneCUETP8M1_13TeV_pythia8')[0]+'\t\t\t'
    text_rate += '\n'

    text_rate += "TotalEvents\t\t\t\t"
    for dataset in datasetList:
        text_rate += str(TotalEventsPerDataset[dataset])
        text_rate += "\t\t\t"
    text_rate = text_rate[:-1]+"\n"
    h.write(text_rate)
    for j in xrange (0,Nlines):
        text_rate = ""
        text_rate += str(rateList[0][j])
        text_rate += "\t"

        text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
        text_rate += "\t+/-\t"
        text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
        text_rate += "\t"
        for i in xrange(0,len(datasetList)):
            if rateList[2*i+3][0]==0:
                rate = 0
                error = 0
            else:
                rate = rateList[2*i+3][j]*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
                error = math.sqrt(rateList[2*i+4][j])*rateDataset[datasetListFromFile[i]]*File_Factor*lumiSF
            text_rate += str(rate)
            text_rate += "\t+/-\t"
            text_rate += str(error)
            text_rate += "\t"
    
        text_rate = text_rate[:-1]+"\n"
        h.write(text_rate)
    h.close()

def WriteRates_Correlation(input_dir,output_dir,output_name,keyWord,type_in='',elementlist_1=[],elementlist_2=[],Plot=False):
    (Nlines,rateList,TotalRateList,TotalErrorList,rateDataset,rateDataset_total,TotalEventsPerDataset,datasetListFromFile)=ReadRates(input_dir,keyWord)
    h = open(output_dir+'/'+output_name, "w")
    text_rate_title = '\t'
    #print elementlist
    for elem in elementlist_2:
        text_rate_title += elem + "\t"
    text_rate_title += '\n'
    h.write(text_rate_title)
    #text_rate = ''
    for elem_1 in elementlist_1:
        text_rate=elem_1+"\t"
        for elem_2 in elementlist_2:
            tmp_list = rateList[0]
            j=rateList[0].index(str((elem_1,elem_2)))
            text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
#            text_rate += "\t+/-\t"
#            text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
            text_rate += "\t"
        text_rate = text_rate[:-1]+"\n"
        h.write(text_rate)
    h.close()
    if Plot:
        import ROOT
        lenth_1 = len(elementlist_1)
        lenth_2 = len(elementlist_2)
        c1 = ROOT.TCanvas( 'c1', 'A Simple 2D Histogram', 800,640 )
        c1.SetLeftMargin(0.2)
        c1.SetRightMargin(0.1)
        c1.SetBottomMargin(0.2)
        CorelHisto = ROOT.TH2F('DatasetCorrelHisto','Overlapping rates for %s pairs'%(type_in), lenth_2, 0, lenth_2, lenth_1, 0, lenth_1)
        n=1
        for elem_2 in elementlist_2:
            CorelHisto.GetXaxis().SetBinLabel(n,elem_2)
            CorelHisto.GetXaxis().LabelsOption("v")
            n+=1
        n=1
        for elem_1 in elementlist_1:
            CorelHisto.GetYaxis().SetBinLabel(n,elem_1)
            CorelHisto.GetYaxis().LabelsOption("v")
            n+=1
        i=1
        for elem_1 in elementlist_1:
            j=1
            for elem_2 in elementlist_2:
                k=rateList[0].index(str((elem_1,elem_2)))
                tmp_value = TotalRateList[k]*rateDataset_total*File_Factor*lumiSF
                CorelHisto.SetBinContent(j,i,tmp_value)
                j+=1
            i+=1
        CorelHisto.SetStats(0)
        ROOT.gStyle.SetPaintTextFormat("0.1f")
        CorelHisto.SetMarkerSize(1.0)
        CorelHisto.Draw("COLZ TEXT")
        c1.Print("%s/CorelationRate_%s.png"%(output_dir,type_in))
        time.sleep(1)
        
def WriteRates_Correlation_2(input_dir,output_dir,output_name,keyWord,type_in='',elementlist_1=[],elementlist_2=[],Plot=False):
    (Nlines,rateList,TotalRateList,TotalErrorList,rateDataset,rateDataset_total,TotalEventsPerDataset,datasetListFromFile)=ReadRates(input_dir,keyWord)
    h = open(output_dir+'/'+output_name, "w")
    text_rate_title = '\tDataset\t'
    #print elementlist
    for elem in elementlist_2:
        text_rate_title += elem + "\t"
    text_rate_title += '\n'
    h.write(text_rate_title)
    #text_rate = ''
    for elem_1 in elementlist_1:
        text_rate=elem_1+"\t"+triggersDatasetMap[elem_1][0]+"\t"
        for elem_2 in elementlist_2:
            tmp_list = rateList[0]
            j=rateList[0].index(str((elem_1,elem_2)))
            text_rate += str(TotalRateList[j]*rateDataset_total*File_Factor*lumiSF)
#            text_rate += "\t+/-\t"
#            text_rate += str(TotalErrorList[j]*rateDataset_total*File_Factor*lumiSF)
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

WriteRates("../ResultsBatch/ResultsBatch_groupEvents/","../Results/","output.group.tsv",'matrixEvents_groups_')
#WriteRates("../ResultsBatch/ResultsBatch_Pure_groupEvents/","../Results/","output.puregroup.tsv",'matrixEvents_Pure_groups_')
WriteRates("../ResultsBatch/ResultsBatch_primaryDatasetEvents/","../Results/","output.dataset.tsv",'matrixEvents_primaryDataset_')
#WriteRates("../ResultsBatch/ResultsBatch_Pure_primaryDatasetEvents/","../Results/","output.puredataset.tsv",'matrixEvents_Pure_primaryDataset_')
WriteRates("../ResultsBatch/ResultsBatch_streamEvents/","../Results/","output.stream.tsv",'matrixEvents_stream_')
#WriteRates("../ResultsBatch/ResultsBatch_Pure_streamEvents/","../Results/","output.purestream.tsv",'matrixEvents_Pure_Stream_')
#WriteRates("../ResultsBatch/ResultsBatch_Exclusive_groupEvents/","../Results/","output.exclgroup.tsv",'matrixEvents_Exclusive_groups_')
#WriteRates_Correlation("../ResultsBatch/ResultsBatch_Core_primaryDatasetEvents/","../Results/","output.matrix_coredataset.tsv",'matrixEvents_Core_primaryDataset_',"dataset",pure_primaryDatasetList,pure_primaryDatasetList,True)
#WriteRates_Correlation_2("../ResultsBatch/ResultsBatch_Core_TriggerDatasetEvents/","../Results/","output.matrix_coretriggerdataset.tsv",'matrixEvents_Core_TriggerDataset_',"trigger_dataset",triggerList,primaryDatasetList,False)


my_print(datasetList)

