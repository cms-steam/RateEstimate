
triggersToRemove = [
    'DST_*',
    'AlCa_*',
    'HLT_EcalCalibration_v',
    'HLT_HcalCalibration_v',
    'HLT_HT410to430_v',
    'HLT_HT430to450_v',
    'HLT_HT450to470_v',
    'HLT_HT470to500_v',
    'HLT_HT500to550_v',
    'HLT_HT550to650_v',
    'HLT_HT650_v',
    'HLT_L1FatEvents_part0_v',
    'HLT_L1FatEvents_part1_v',
    'HLT_L1FatEvents_part2_v',
    'HLT_L1FatEvents_part3_v',
    'HLT_L1FatEvents_v',
    'HLT_Physics_v',
    'HLT_Random_v'
    
]


#triggersGroupMap = dict(triggersGroupMap.items())

triggerList = []
L1List = []
HLTList = []
#twoHLTsList = []
primaryDatasetList = []
groupList = []
twoDatasetsList = []
getTriggerString = {}

## Fill triggerList and groupList and primaryDatasetList
for trigger in triggersDatasetMap.keys():
    #if trigger[:-1] in triggersToRemove: continue
    if not (trigger in triggerList) : triggerList.append(trigger)
    for dataset in triggersDatasetMap[trigger]:
        if not dataset in primaryDatasetList: primaryDatasetList.append(dataset)
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove): continue
    for group in triggersGroupMap[trigger]:
        if not group in groupList: groupList.append(group)

## Fill HLTList and L1List
for trigger in triggerList:
    if "HLT_" in trigger: HLTList.append(trigger)
#    elif "L1_" in trigger: L1List.append(trigger)

## Fill getTriggerString get a map from trigger and group names to strings
for trigger in triggerList:
    getTriggerString[trigger]=trigger
    for dataset in triggersDatasetMap[trigger]:
        if dataset in getTriggerString.keys(): getTriggerString[dataset]+='||'+trigger
        else: getTriggerString[dataset]=trigger
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove):
        print trigger
        continue
    for group in triggersGroupMap[trigger]:
        if group in getTriggerString.keys(): getTriggerString[group]+='||'+trigger
        else: getTriggerString[group]=trigger

## Fill string for All group
groupList.append('All_HLT')
for trigger in HLTList:
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove): continue
    if 'All_HLT' in getTriggerString.keys(): getTriggerString['All_HLT']+='||'+trigger
    else: getTriggerString['All_HLT']=trigger

## Fill string for prescaled paths
groupList.append('All_PSed')
for trigger in HLTList:
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove): continue
    if int(prescaleMap[trigger][0]) <=1 : continue
    if 'All_PSed' in getTriggerString.keys(): getTriggerString['All_PSed']+='||'+trigger
    else: getTriggerString['All_PSed']=trigger

## Fill string for type
groupList.append('type_signal')
for trigger in triggersTypeMap:
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove): continue
    if (not ('signal' in triggersTypeMap[trigger])) and (not ('backup' in triggersTypeMap[trigger])):continue
    if 'type_signal' in getTriggerString.keys(): getTriggerString['type_signal']+='||'+trigger
    else: getTriggerString['type_signal']=trigger

groupList.append('type_control')
for trigger in triggersTypeMap:
    if (trigger in triggersToRemove) or (trigger[:-1] in triggersToRemove) or (trigger.split('_')[0]+'_*' in triggersToRemove): continue
    if not ('control' in triggersTypeMap[trigger]):continue
    if 'type_control' in getTriggerString.keys(): getTriggerString['type_control']+='||'+trigger
    else: getTriggerString['type_control']=trigger

#groupList.append('type_backup')
#for trigger in triggersTypeMap:
#    if not ('backup' in triggersTypeMap[trigger]):continue
#    if 'type_backup' in getTriggerString.keys(): getTriggerString['type_backup']+='||'+trigger
#    else: getTriggerString['type_backup']=trigger

                                           
