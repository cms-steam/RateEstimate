#! /usr/bin/env python
 # -*- coding: UTF-8 -*

########## Configuration ##############################################
# L1 Menu name
nameMenu = "L1Menu_Collisions2015_25nsStage1_v5"
# Link to L1 Menu google-doc
linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1zxnRwLNEQPuzcZ6qDkXBv6Ctmbq9LN9zQK6O6DIv8qg/edit#gid=0"
#"https://docs.google.com/spreadsheets/d/1zxnRwLNEQPuzcZ6qDkXBv6Ctmbq9LN9zQK6O6DIv8qg/edit#gid=0"
###################################################################
download = True

nameMenu = nameMenu.replace("\\","_")
nameMenu = nameMenu.replace("/","_")
nameMenu = nameMenu.replace(" ","_")
nameMenu = nameMenu.replace(".","p")

import os,sys

if download:
    ### Download the googleDOC in .tsv format ###
    if "edit#gid=0" in linkToGoogleDOC:
        linkToGoogleDOC = linkToGoogleDOC[:-10]

    linkToGoogleDOCsplitted=linkToGoogleDOC.split("/")
    code = linkToGoogleDOCsplitted[len(linkToGoogleDOCsplitted)-2]
    linkToGoogleDOCtsv = linkToGoogleDOC + "export?format=tsv&id=" + code + "&gid=0"
    command = 'wget -O tmp/'+nameMenu+".tsv "+linkToGoogleDOCtsv
    print command
    os.popen(command,'r').read()

### Read the googleDOC in .tsv format ###
output = "triggersGroupMap_"+nameMenu
lines = open("tmp/"+nameMenu+".tsv")
tmp = open("tmp/tmp.py","w")
fileOut = open("config/"+output+".py","w")

comment=""
count=0
idx_path=-1
idx_mask=-1
idx_group0=-1
idx_group1=-1 
idx_group2=-1 
idx_group3=-1 
idx_group4=-1 
idx_group5=-1 
idx_group6=-1 
#idx_scenario=-1
triggerMap={}
allgroups=set()
alltriggers=set()
for line in lines:
    if(count<2): comment+=line
    if ('Path' in line) and (idx_path<0):
        words=line.split("\t")
        for word in words:
            if(word=="Path"): idx_path = words.index(word)
            if(word=="mask"): idx_mask = words.index(word)
            if(word=="Emergency"): idx_group0 = words.index(word)
            if(word=="1e34"): idx_group1 = words.index(word) 
            if(word=="7e33"): idx_group2 = words.index(word) 
            if(word=="5e33"): idx_group3 = words.index(word) 
            if(word=="3.5e33"): idx_group4 = words.index(word) 
            if(word=="2e33"): idx_group5 = words.index(word) 
            if(word=="1e33"): idx_group6 = words.index(word) 
    
    count+=1
    if not('L1_' in line): continue
    words = line.split("\t")

    trigger = words[idx_path]
    alltriggers.add(trigger)

    if(words[idx_mask]=="0"):
        maskString = 'L1'
    else: maskString = 'Masked'    
    
    groupString0 = words[idx_group0] 
    groupString1 = words[idx_group1] 
    groupString2 = words[idx_group2] 
    groupString3 = words[idx_group3] 
    groupString4 = words[idx_group4] 
    groupString5 = words[idx_group5] 
    groupString6 = words[idx_group6] 

    triggerMap[trigger]=(maskString,groupString0,groupString1,groupString2,groupString3,groupString4,groupString5,groupString6)
#   Use the following instead for the standard work flow:
#   triggerMap[trigger]=maskString    

lines.close()

print >> tmp, triggerMap
tmp.close()
tmp = open("tmp/tmp.py","r")
#comment = comment.replace('\n', '\n#')
#comment = comment.replace('\t', ' ')
#comment = comment[:-1]
fileOut.write("#"+nameMenu+"\n")
fileOut.write('\n')
fileOut.write("triggersL1GroupMap = ")
for line in tmp:
 #   line = line.replace('\',', '\',\n}')
    line = line.replace('), ', '],\n\t')
    line = line.replace(')', ']\n') 
    line = line.replace(': (', ': [')
    line = line.replace('{', '{\n\t')
    line = line.replace('}', '\n}')
    fileOut.write(line)
fileOut.write('\n')
tmp.close()

fileOut.close()
