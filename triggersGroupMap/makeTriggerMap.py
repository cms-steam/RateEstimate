file_menu = 'Fill_5105_Menu.tsv'
file_sample = 'config/triggerDatasetMapTail.py'
file_output = 'Fill_5105_Menu.py'
triggerName = 'tttt'
column_stream = 0
column_dataset = 1
column_trigger = 2
column_group = 3
column_type = 4
column_ps = 77

triggerDataset = {}
triggerStream = {}
triggerGroup = {}
triggerType = {}
prescaleMap = {}

current_stream = ''
current_dataset = ''


for Line in open(file_menu,'r'):
    line = Line.split('\t')
    if 'stream' in line[column_stream]:
        current_stream = line[column_stream].replace('stream','')
        current_stream = current_stream.replace(' ','')
        continue
    if 'dataset' in line[column_dataset]:
        current_dataset = line[column_dataset].replace('dataset','')
        current_dataset = current_dataset.replace(' ','')
        continue
    if '_v' in line[column_trigger]:
        trigger = line[column_trigger]
# make stream map
        if not (trigger in triggerStream):
            tmp_list = []
            tmp_list.append(current_stream)
            triggerStream[trigger] = tmp_list
        else:
            if not (current_stream in triggerStream[trigger]):
                triggerStream[trigger].append(current_stream)

# make dataset map
        if not (trigger in triggerDataset):
            tmp_list = []
            tmp_list.append(current_dataset)
            triggerDataset[trigger] = tmp_list
        else:
            if not (current_dataset in triggerDataset[trigger]):
                triggerDataset[trigger].append(current_dataset)
# make group map
        tmp_group = line[column_group]
        tmp_group = tmp_group.replace('/',',')
        tmp_group = tmp_group.replace('(',',')
        tmp_group = tmp_group.replace(')',',')
        tmp_group = tmp_group.replace(' ','')
        tmp_group = tmp_group.replace('SUSY','SUS')
        tmp_group = tmp_group.replace('Muon','MUO')
        tmp_group = tmp_group.replace('muon','MUO')
        tmp_group_list = tmp_group.split(',')
        if not (trigger in triggerGroup):
            triggerGroup[trigger] = tmp_group_list 
# make PS map
        if not (trigger in prescaleMap):
            tmp_list = []
            prescale = line[column_ps]
	    prescale = prescale.replace('\n','')
            prescale = prescale.replace('\r','')
            prescale = prescale.replace('\d','')
            prescale = prescale.replace(' ','')
            prescale = prescale.replace(',','.')
            tmp_list.append(str(int(float(prescale))))
            prescaleMap[trigger] = tmp_list

# make type map
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

# write the rest part (from sample)
for line in open(file_sample,'r'):
    file_out.write(line)
