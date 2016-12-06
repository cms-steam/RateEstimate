file_menu = 'HLT_Menu_v4.2_v6.tsv'
file2_L1menu = 'HLT_Menu_v4.2_v6_L1_v9.tsv'
file_sample = 'config/triggerDatasetMapTail_L1.py'
file_output = 'HLT_Menu_v4p2_v6_L1_v9.py'
triggerName = 'tttt'
column_stream = 0
column_dataset = 1
column_trigger = 2
column_group = 4
column_type = -1
column_ps = 10
column_L1Seed = 24 

column2_L1trigger = 1 
column2_L1ps = 6
use_prescaled_ntuples = True

triggerDataset = {}
triggerStream = {}
triggerGroup = {}
triggerType = {}
prescaleMap = {}
streamDataset = {}
datasetStream = {}

current_stream = ''
current_dataset = ''

def MatchL1Seed(l1seed):
    tmp_list=[]
    i_last = 0
    L1_start = False
    L1_list = []
    for i in range(len(l1seed)):
        if i<3:continue
       # print l1seed[i-3:i]
        if l1seed[i-3:i]=='L1_' and L1_start==False:
            L1_start=True
            #tmp_list.append(l1seed[i_last:i-3])
            i_last=i-3
        if (l1seed[i]==' ' or l1seed[i]=='|' or l1seed[i]==')') and L1_start==True:
            L1_start=False
            tmp_list.append(l1seed[i_last:i])
            i_last=i
        if i==len(l1seed)-1 and L1_start == True:
            tmp_list.append(l1seed[i_last:i+1])
    return tmp_list

def getL1prescale(filename, column_path, column_ps):
    prescale_dic = {}
    tmp_file = open(filename, "r")
    for Line in tmp_file:
        line = Line.split('\t')
        if "L1_" in line[column_path]:
            prescale = line[column_ps]
            prescale = prescale.replace('\n','')
            prescale = prescale.replace('\r','')
            prescale = prescale.replace('\d','')
            prescale = prescale.replace(' ','')
            prescale = prescale.replace(',','.')
            tmp_ps = float(prescale)
            if (tmp_ps !=0 and tmp_ps <1) or use_prescaled_ntuples:
                tmp_ps = 1
            prescale_dic[line[column_path]] = []
            prescale_dic[line[column_path]].append(str(int(tmp_ps)))
    return prescale_dic

def check_group(group):
    group_list =['EXO', 'JME', 'SUS', 'BPH', 'SMP', 'BTV', 'TAU', 'HIG', 'EGM', 'B2G', 'MUO', 'PPD', 'AlCa', 'TOP', 'HIN', 'TRK', 'FSQ', 'ECAL', 'HCAL', 'null', 'All_HLT', 'All_PSed', 'type_signal', 'type_control','Higgs','Analysis','tau-pog','Egamma','ttH']
    if group in group_list:
        return True
    isGroup = True
    if (len(group)<3 or len(group)>10)and isGroup:
        isGroup = False
    if isGroup:
        if not group[0].isupper():
            isGroup = False
#        if not group[1].isupper():
#            isGroup = False
    return isGroup


# make PS map
prescaleMap = getL1prescale(file2_L1menu, column2_L1trigger, column2_L1ps)
for Line in open(file_menu,'r'):
    line = Line.split('\t')
    trigger = ''
    if column_stream >=0:
        if 'stream' in line[column_stream]:
            current_stream = line[column_stream].replace('stream','')
            current_stream = current_stream.replace('\n','')
            current_stream = current_stream.replace(' ','')
            if not current_stream in streamDataset:
                streamDataset[current_stream]=[]
            continue
    if column_dataset >=0:
        if 'dataset' in line[column_dataset]:
            current_dataset = line[column_dataset].replace('dataset','')
            current_dataset = current_dataset.replace('\n','')
            current_dataset = current_dataset.replace(' ','')
            if not current_dataset in streamDataset[current_stream]:
                streamDataset[current_stream].append(current_dataset)
            if column_stream >=0:
                datasetStream[current_dataset]=current_stream
            continue
    if column_trigger >=0:
        if '_v' in line[column_trigger]:
            trigger_list = MatchL1Seed(line[column_L1Seed])
            print trigger_list
        else:continue
    for trigger in trigger_list:
    # make stream map
        if column_stream >=0:
            if not (trigger in triggerStream):
                tmp_list = []
                tmp_list.append(current_stream)
                triggerStream[trigger] = tmp_list
            else:
                if not (current_stream in triggerStream[trigger]):
                    triggerStream[trigger].append(current_stream)
    
    # make dataset map
        if column_dataset >=0:
            if not (trigger in triggerDataset):
                tmp_list = []
                tmp_list.append(current_dataset)
                triggerDataset[trigger] = tmp_list
            else:
                if not (current_dataset in triggerDataset[trigger]):
                    triggerDataset[trigger].append(current_dataset)
    # make group map
        if column_group >=0:
            tmp_group = line[column_group]
            tmp_group = tmp_group.replace('/',',')
            tmp_group = tmp_group.replace('(',',')
            tmp_group = tmp_group.replace(')',',')
            tmp_group = tmp_group.replace('-',',')
            tmp_group = tmp_group.replace('.',',')
            tmp_group = tmp_group.replace('SUSY','SUS')
            tmp_group = tmp_group.replace('Higgs','HIG')
            tmp_group = tmp_group.replace('Egamma','EGM')
            tmp_group = tmp_group.replace('EXO PAG','EXO,PAG')
            tmp_group = tmp_group.replace('B2G PAG','B2G,PAG')
            tmp_group = tmp_group.replace('Muon','MUO')
            tmp_group = tmp_group.replace('muon','MUO')
            tmp_group = tmp_group.replace('tau pog','tau-pog')
            tmp_group = tmp_group.replace(' ','')
            tmp_group_list = tmp_group.split(',')
            tmp_group_list2 = []
            if not (trigger in triggerGroup):
                for group in tmp_group_list:
                    group=group.strip(' ')
                    if check_group(group):
                        tmp_group_list2.append(group)
                if tmp_group_list2 == []:
                    tmp_group_list2 = [' ']
                triggerGroup[trigger] = tmp_group_list2 
            else:
                for group in tmp_group_list:
                    if not group in triggerGroup[trigger]:
                        triggerGroup[trigger].append(group)
    
    # make type map
        if column_type >=0:
            if not (trigger in triggerType):
                tmp_list = []
                tmp_list.append(line[column_type])
                triggerType[trigger] = tmp_list
            else:
                if not (line[column_type] in triggerType[trigger]):
                    triggerType[trigger].append(line[column_type])


# write to output triggerMap.py
file_out = open(file_output,'w')

file_out.write('# -*- coding: iso-8859-15 -*-\n')
file_out.write('triggerList = []\n')
file_out.write('triggerName = "%s"\n'%(triggerName))

# write dataset
file_out.write('triggersDatasetMap = {\n')
for trigger in triggerDataset:
    file_out.write('    \'%s\' : %s,\n'%(trigger,triggerDataset[trigger]))
file_out.write('}\n\n')
# write group
file_out.write('triggersGroupMap = {\n')
for trigger in triggerGroup:
    file_out.write('    \'%s\' : %s,\n'%(trigger,triggerGroup[trigger]))
file_out.write('}\n\n')
# write stream
file_out.write('DatasetStreamMap = {\n')
for trigger in triggerStream:
    file_out.write('    \'%s\' : %s,\n'%(trigger,triggerStream[trigger]))
file_out.write('}\n\n')
# write ps information
file_out.write('prescaleMap = {\n')
for trigger in prescaleMap:
    file_out.write('    \'%s\' : %s,\n'%(trigger,prescaleMap[trigger]))
file_out.write('}\n\n')
# write type information
file_out.write('triggersTypeMap = {\n')
for trigger in triggerType:
    file_out.write('    \'%s\' : %s,\n'%(trigger,triggerType[trigger]))
file_out.write('}\n\n')
# write stream: dataset
file_out.write('streamDataset = {\n')
for stream in streamDataset:
    file_out.write('    \'%s\' : %s,\n'%(stream,streamDataset[stream]))
file_out.write('}\n\n')
# write dataset: stream
file_out.write('datasetStream = {\n')
for dataset in datasetStream:
    file_out.write('    \'%s\' : "%s",\n'%(dataset,str(datasetStream[dataset])))
file_out.write('}\n\n')


# write the rest part (from sample)
for line in open(file_sample,'r'):
    file_out.write(line)
