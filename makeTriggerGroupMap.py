#! /usr/bin/env python
 # -*- coding: UTF-8 -*-

########## Configuration ##############################################
### 50ns example ###
nameMenu = "/frozen/2015/50ns_5e33/v2.1/HLT/V5"
linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1xeifxX9oZUT47GDjyepvGgPPIzV333Txf8BD4FnHTyc/edit#gid=0"       #link to 50ns frozen menu (16/06/2015)
L1Triggers = "triggersGroupMap_L1Menu_Collisions2015_50nsGct_v3.py"

### 25ns example ###
#nameMenu = "/frozen/2015/25ns14e33/v2.0/HLT/V1"
#linkToGoogleDOC="https://docs.google.com/spreadsheets/d/1OGcjnJdkwh_ysNhnvf2jv-It2xruG5DpsDgMXNcc7d4/edit#gid=0"       #link to 25ns frozen menu (16/06/2015)
#L1Triggers = "triggersGroupMap_L1Menu_Collisions2015_25nsStage1_v3.py"
###################################################################
download = True

nameMenu = nameMenu.replace("\\","_")
nameMenu = nameMenu.replace("/","_")
nameMenu = nameMenu.replace(" ","_")
nameMenu = nameMenu.replace(".","_")

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
    splitted = groupString.split(",")
    if splitted[0]=="":
        splitted=["NoGroup"]
    
    return splitted

import os,sys

if download:
    ### Download the googleDOC in .tsv format ###
    if "edit#gid=0" in linkToGoogleDOC:
        linkToGoogleDOC = linkToGoogleDOC[:-10]

    linkToGoogleDOCsplitted=linkToGoogleDOC.split("/")
    code = linkToGoogleDOCsplitted[len(linkToGoogleDOCsplitted)-2]
    linkToGoogleDOCtsv = linkToGoogleDOC + "export?format=tsv&id=" + code + "&gid=0"
    command = 'wget -O '+nameMenu+".tsv "+linkToGoogleDOCtsv
    print command
    os.popen(command,'r').read()

### Read the googleDOC in .tsv format ###
output = "triggersGroupMap_"+nameMenu
lines = open(nameMenu+".tsv")
tmp = open("tmp.py","w")
fileOut = open(output+".py","w")

comment=""
count=0
idx_path=-1
idx_group=-1
triggerMap={}
allgroups=set()
alltriggers=set()
for line in lines:
    if(count<2): comment+=line
    if ('Path' in line) and (idx_path<0):
        words=line.split("\t")
        for word in words:
            if(word=="Path"): idx_path = words.index(word)
            if(word=="Group"): idx_group = words.index(word)
    
    count+=1
    if not('HLT_' in line): continue
    words = line.split("\t")
    trigger = words[idx_path]
    alltriggers.add(trigger)
    groupString = words[idx_group]
    groups = getGroups(groupString)
    triggerMap[trigger]=groups
    for group in groups:
        allgroups.add(group)

lines.close()
print "Groups:"
for group in allgroups:
    print group

print >> tmp, triggerMap
tmp.close()
tmp = open("tmp.py","r")
comment = comment.replace('\n', '\n#')
comment = comment.replace('\t', ' ')
comment = comment[:-1]
fileOut.write("#"+comment)

fileOut.write('\ntriggerList = []\n')
fileOut.write('triggerName = "'+nameMenu+'"\n')
fileOut.write('\n')
fileOut.write("triggersGroupMap = ")
for line in tmp:
    line = line.replace('], ', '],\n\t')
    line = line.replace('{', '{\n\t')
    line = line.replace('}', '\n}')
    fileOut.write(line)
fileOut.write('\n')
tmp.close()
L1TriggersFile = open(L1Triggers,"r")
for line in L1TriggersFile:
    fileOut.write(line)
L1TriggersFile.close
tail = open("triggerGroupMapTail.py","r")
for line in tail:
    fileOut.write(line)
tail.close()
fileOut.close()
