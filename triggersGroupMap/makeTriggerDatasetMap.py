#! /usr/bin/env python
 # -*- coding: UTF-8 -*

########## Configuration ##############################################

### 25ns example from frozen 25ns GoogleDOC menu ###
#nameMenu = "/frozen/2015/25ns14e33/v3.3/HLT/V2"
nameMenu = "GRun_V58/modifiable"
#linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1BkgAHCC4UtP5sddTZ5G5iWY16BxleuK7rqT-Iz2LHiM/edit#gid=0"       #link to 25ns frozen menu (17/08/2015)
linkToGoogleDOC="https://docs.google.com/spreadsheets/d/14niSkIWrug2HSgN-ddrpk5TF2S8zFeHkopjxHAnb7nk/edit#gid=1670905758"
L1Triggers = "config/triggersGroupMap_L1Menu_Collisions2015_25nsStage1_v3.py"

#### 50ns example from frozen 50ns GoogleDOC menu ###
#nameMenu = "online/collisions/2015/50ns_5e33/v3.4/HLT/V2"
#linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1MTMNz-edWykho59_zBiSu24L7FeNV0WprG7_YdULntw/edit#gid=0"       #link to 50ns frozen menu (17/08/2015)
#L1Triggers = "config/triggersGroupMap_L1Menu_Collisions2015_50nsGct_v4.py"

## 25ns example from "development" GoogleDOC menu ###
#nameMenu = "/dev/CMSSW_7_4_0/HLT/V382"
#linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1AVAiNLvQZVVuDC0mOt7xZqzcUxJ5dv-9mjLui6m7fz4/edit#gid=0"       #link to development menu (17/08/2015)
#L1Triggers = "config/triggersGroupMap_L1Menu_Collisions2015_50nsGct_v4.py"
#scenario = "25ns"       #select scenario to use in the development menu

###################################################################
download = True
nameMenu = nameMenu.replace("\\","_")
nameMenu = nameMenu.replace("/","_")
nameMenu = nameMenu.replace(" ","_")
nameMenu = nameMenu.replace(".","p")

if not('scenario' in vars() or 'scenario' in globals()): scenario = ""
if not scenario=="":
    nameMenu = nameMenu + "_"+scenario

def getGroups(groupString):
    groupString=groupString.replace(" ","")
    groupString=groupString.replace("(","")
    groupString=groupString.replace(")","")
    groupString=groupString.replace("Higgs","HIG")
    groupString=groupString.replace("Hbb","HIG")
    groupString=groupString.replace("HIGHIG","HIG")
    groupString=groupString.replace("long-lived","")
    groupString=groupString.replace("doublemu","")
    groupString=groupString.replace("H->4b","")
    groupString=groupString.replace("nobptx","")
    groupString=groupString.replace("H→ZZ→2ℓ2ν","")
    groupString=groupString.replace("H2taus","")
    groupString=groupString.replace("E/Gamma","Egamma")
    groupString=groupString.replace("Jets/MET","JME")
    groupString=groupString.replace("Top","TOP")
    groupString=groupString.replace("Tau","TAU")
    groupString=groupString.replace("TAUs","TAU")
    groupString=groupString.replace("H→4b","")
    groupString=groupString.replace("H→ττ","")
    groupString=groupString.replace("#N/A","NoGroup")
    splitted = groupString.split(",")
    if splitted[0]=="":
        splitted=["NoGroup"]
    
    return splitted

import os,sys

if download:
    ### Download the googleDOC in .tsv format ###
#    if "edit#gid=0" in linkToGoogleDOC:
#        linkToGoogleDOC = linkToGoogleDOC[:-10]

    linkToGoogleDOCsplitted=linkToGoogleDOC.split("/")
    code = linkToGoogleDOCsplitted[len(linkToGoogleDOCsplitted)-2]
    print "CODE :",code
    lastDigits = linkToGoogleDOCsplitted[len(linkToGoogleDOCsplitted)-1].split("=")
    print lastDigits[1]
    linkToGoogleDOCtsv = ""
    for i in xrange(0,len(linkToGoogleDOCsplitted)-1):
        linkToGoogleDOCtsv += linkToGoogleDOCsplitted[i]+"/"
    linkToGoogleDOCtsv += "export?format=tsv&id=" + code + "&gid="+str(lastDigits[1])
    print linkToGoogleDOCtsv
    command = 'wget -O tmp/'+nameMenu+".tsv "+linkToGoogleDOCtsv
    print command
    os.popen(command,'r').read()

### Read the googleDOC in .tsv format ###
output = "triggersGroupMap_"+nameMenu
lines = open("tmp/"+nameMenu+".tsv")
tmp = open("tmp/tmp.py","w")
tmpGroup = open("tmp/tmpGroup.py","w")
tmpStream = open("tmp/tmpStream.py","w")
fileOut = open(output+".py","w")

comment=""
count=0
idx_path=-1
idx_group=-1
idx_scenario=-1
foundGroup = False
triggerList = []
triggerMap={}
triggerGroupMap={}
datasetMap={}
allgroups=set()
alltriggers=set()
stream = ""
dataset = ""
for line in lines:
    if(count<2):
        count+=1
        continue
    words=line.split("\t")
    
    for word in words:
        if("Group" in word):
            idx_group = words.index(word)
            foundGroup = True
            print idx_group
        elif('stream' in word):
            subword=word.split(" ")
            stream = subword[1]
            if foundGroup: break
            else: continue
        elif('dataset' in word):
            subword=word.split(" ")
            dataset = subword[1]
            datasetMap[dataset]=stream
            break
        else:
            if not foundGroup: continue
            if word!= "":
                trigger = word
                if trigger not in triggerList:
                    triggerList.append(trigger)
                    triggerMap[trigger]=dataset
                    triggerGroupMap[trigger] = "null"
                else: triggerMap[trigger]+=','+dataset
                break

for trigger in triggerGroupMap.keys():
    triggerGroupMap[trigger] = triggerGroupMap[trigger].split(",")    
for dataset in datasetMap.keys():
    datasetMap[dataset] = datasetMap[dataset].split(",")
for trigger in triggerMap.keys():
    triggerMap[trigger] = triggerMap[trigger].split(",") 

#for trigger in triggerMap.keys():
#    print trigger,":",triggerMap[trigger]

#    if ('Path' in line) and (idx_path<0):
#        words=line.split("\t")
#        for word in words:
#            if(word=="Path"): idx_path = words.index(word)
#            if(word=="Group"): idx_group = words.index(word)
#            if(word=="Scenario"): idx_scenario = words.index(word)
#    

#    if not('HLT_' in line): continue
#    words = line.split("\t")
#    if idx_scenario>=0:
#        if not(scenario in words[idx_scenario]): continue
#    trigger = words[idx_path]
#    alltriggers.add(trigger)
#    groupString = words[idx_group]
#    groups = getGroups(groupString)
#    triggerMap[trigger]=groups
#    for group in groups:
#        allgroups.add(group)
    #print trigger,groupString
lines.close()
print "Datasets:"
for dataset in datasetMap.keys():
    print dataset

print >> tmp, triggerMap
tmp.close()
print >> tmpGroup, triggerGroupMap
tmpGroup.close()
print >> tmpStream, datasetMap
tmpStream.close()
tmp = open("tmp/tmp.py","r")
tmpGroup = open("tmp/tmpGroup.py","r")
tmpStream = open("tmp/tmpStream.py","r")
#comment = comment.replace('\n', '\n#')
#comment = comment.replace('\t', ' ')
#comment = comment[:-1]
fileOut.write("# -*- coding: iso-8859-15 -*-")
#fileOut.write("#"+comment)

fileOut.write('\ntriggerList = []\n')
fileOut.write('triggerName = "'+nameMenu+'"\n')
fileOut.write('\n')
fileOut.write("triggersDatasetMap = ")
for line in tmp:
    line = line.replace('], ', '],\n\t')
    line = line.replace('{', '{\n\t')
    line = line.replace('}', '\n}')
    fileOut.write(line)
fileOut.write('\n')
tmp.close()
fileOut.write("triggersGroupMap = ")
for line in tmpGroup:
    line = line.replace('], ', '],\n\t')
    line = line.replace('{', '{\n\t')
    line = line.replace('}', '\n}')
    fileOut.write(line)
fileOut.write('\n')
tmpGroup.close()
fileOut.write("datasetStreamMap = ")
for line in tmpStream:
    line = line.replace('], ', '],\n\t')
    line = line.replace('{', '{\n\t')
    line = line.replace('}', '\n}')
    fileOut.write(line)
fileOut.write('\n')
tmpStream.close()
#L1TriggersFile = open(L1Triggers,"r")
#for line in L1TriggersFile:
#    fileOut.write(line)
#L1TriggersFile.close
tail = open("config/triggerDatasetMapTail.py","r")
for line in tail:
    fileOut.write(line)
tail.close()
fileOut.close()
