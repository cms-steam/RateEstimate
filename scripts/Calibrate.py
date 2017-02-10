import os
import ROOT
file_new = "triggersGroupMap/Menu_online_v3p1_V4_Evaluate_Rates.py"
#file_new = "triggersMap_GRun_V112.py"
tsv_file = open("triggersGroupMap/Menu_online_v3.1_V4_Evaluate_Rates.tsv","r")

column_pre = 4
column_path = 2
output_map = {}

def getTrigger(filename):
    my_dic={}
    _file0 = ROOT.TFile.Open(filename)
    chain = ROOT.gDirectory.Get("HltTree")

    for leaf in chain.GetListOfLeaves():
        name = leaf.GetName()
        if not ("Prescl" in name):
            trigger=name
            my_dic[trigger]=trigger
    return my_dic

triggerNtuples = getTrigger('hltbits_100.root')
lines = tsv_file.readlines()
for line in lines:
    line = line.replace('\r\n','')
    lineTSV = line.split('\t')
    path = lineTSV[column_path].split(' ')[0]
    if path =='': continue
    if not '_' in path:continue
    path1 = path.split('_v')[0]+'_v'
    for trigger in triggerNtuples:
        if path1 in trigger and path != trigger:
            os.system("sed -i 's/%s/%s/g' %s"%(path,trigger,file_new))
            print("sed -i 's/%s/%s/g' %s"%(path,trigger,file_new))
