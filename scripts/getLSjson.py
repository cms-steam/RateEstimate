# -*- coding: utf-8 -*-
import time
import sys
sys.path.append("../")
import os  
import csv
import math
from datasetCrossSections.datasetCrossSectionsHLTPhysics import *

def getLS(input_dir, keyWord):
    tmp_dic = {}
    tmp_list = []
    wdir = input_dir
    for LS_file in os.listdir(wdir):
        tmp_file = open(wdir+LS_file,'r')
        for Line in tmp_file:
            line = Line.replace('\n','')
            if not line in tmp_list:
                tmp_list.append(line)
    for line in tmp_list:
        line = line.replace(")","")
        line = line.replace("(","")
        line = line.replace("'","")
        part = line.split(",")
        runnr = str(int(part[1]))
        ls = part[2]
        if not runnr in tmp_dic:
            tmp_dic[runnr] = []
        if not int(ls) in tmp_dic[runnr]:
            tmp_dic[runnr].append(int(ls))
    return tmp_dic

def makeLSjson(input_dic):
    tmp_dic = {}
    for runnr in input_dic:
        ls_list = input_dic[runnr]
        ls_list.sort()
        tmp_dic[runnr] = []
        tmp_list = [0,0]
        sublist_start = False
        previous_i = 0
        for i in range(len(ls_list)):
            if sublist_start and (ls_list[i] - ls_list[previous_i]>1):
                tmp_list[1] = ls_list[previous_i]
                tmp_dic[runnr].append([tmp_list[0],tmp_list[1]])
                sublist_start = False
            if not sublist_start:
                tmp_list[0] = ls_list[i]
                sublist_start = True
            if i == len(ls_list) -1:
                if not sublist_start:
                    tmp_list[0] = ls_list[i]
                    tmp_list[1] = ls_list[i]
                    tmp_dic[runnr].append([tmp_list[0],tmp_list[1]])
                else:
                    tmp_list[1] = ls_list[i]
                    tmp_dic[runnr].append([tmp_list[0],tmp_list[1]])
            previous_i = i
    return tmp_dic

def printjson(input_json,outname):
    tmp_file = open(outname,"w")
    tmp_file.write(str(input_json).replace("'",'"'))               
            

#start~~~~~~~~~~~~~~~~~~~~~~~~~~~~
lumisection_json_dic = getLS("../ResultsBatch/ResultsBatch_LS/",'matrixEvents_HLTPhysics')
print lumisection_json_dic
print makeLSjson(lumisection_json_dic)
#print makeLSjson({"aaa":[1,5,12,13,14,16]})
printjson(makeLSjson(lumisection_json_dic),"1p45_json.txt")
