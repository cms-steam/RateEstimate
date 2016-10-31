#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    'HLT_Physics_v',
    'HLT_L1FatEvents_part0_v',
    'HLT_L1FatEvents_part1_v',
    'HLT_L1FatEvents_part2_v',
    'HLT_L1FatEvents_part3_v',
    'HLT_L1FatEvents_v',
    'HLT_ZeroBias_part0_v',
    'HLT_ZeroBias_part1_v',
    'HLT_ZeroBias_part2_v',
    'HLT_ZeroBias_part3_v',
    'HLT_ZeroBias_part4_v',
    'HLT_Physics_part0_v',
    'HLT_Physics_part1_v',
    'HLT_Physics_part2_v',
    'HLT_Physics_part3_v',
    'HLT_ZeroBias_v',
    'HLT_Random_v',
    'HLT_RsqMR240_Rsq0p09_MR200_4jet_v',
    'HLT_Photon90_CaloIdL_PFHT500_v',
    'HLT_Mu3er_PFHT140_PFMET125_v',
    'HLT_Mu6_PFHT200_PFMET80_BTagCSV_p067_v',
    'HLT_PFMET120_BTagCSV_p067_v',
]

pureDatasetToRemove = [
    'HLTPhysics*',
    'Parking*',
]
def remove_trigger(trigger_in):
    if trigger_in in triggersToRemove:
        return True

    for trigger in triggersToRemove:
        if '*' in trigger:
            if trigger[:-1] in trigger_in:
                return True

        elif '_v' in trigger:
            if trigger.split('_v')[0] == trigger_in.split('_v')[0]:
                return True

        else:
            if trigger == trigger_in.split('_v')[0]:
                return True
    return False

def remove_pure_dataset(dataset_in):
    if dataset_in in pureDatasetToRemove:
        return True
    for dataset in pureDatasetToRemove:
        if '*' in dataset:
            if dataset[:-1] in dataset_in:
                return True
    if (not "Physics" in datasetStream[dataset_in]) or "Parking" in datasetStream[dataset_in]:
        return True
    return False

def remove_pure_stream(stream_in):
    if (not "Physics" in stream_in[:7]):
        return True
    return False

#triggersGroupMap = dict(triggersGroupMap.items())

triggerList = []
pure_triggerList = []
L1List = []
HLTList = []
#twoHLTsList = []
primaryDatasetList = []
pure_primaryDatasetList = []
streamList = []
pure_streamList = []
groupList = []
corelation_datasetList = []
corelation_trigger_datasetList = []
twoDatasetsList = []
getTriggerString = {}

## Fill triggerList and groupList and primaryDatasetList
for trigger in triggersDatasetMap.keys():
    #if trigger[:-1] in triggersToRemove: continue
    if not (trigger in triggerList) : triggerList.append(trigger)
    for dataset in triggersDatasetMap[trigger]:
        if not dataset in primaryDatasetList: primaryDatasetList.append(dataset)
        if (not dataset in pure_primaryDatasetList) and (not remove_pure_dataset(dataset)): 
            pure_primaryDatasetList.append(dataset)
    for stream in DatasetStreamMap[trigger]:
        if not stream in streamList: streamList.append(stream)
        if (not stream in pure_streamList) and (not remove_pure_stream(stream)):
            pure_streamList.append(stream)
    if remove_trigger(trigger):continue
    if not (trigger in pure_triggerList) : pure_triggerList.append(trigger)
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
    for stream in DatasetStreamMap[trigger]:
        if stream in getTriggerString.keys(): getTriggerString[stream]+='||'+trigger
        else: getTriggerString[stream]=trigger
    if remove_trigger(trigger):
        print trigger
        continue
    for group in triggersGroupMap[trigger]:
        if group in getTriggerString.keys(): getTriggerString[group]+='||'+trigger
        else: getTriggerString[group]=trigger

## Fill string for All group
groupList.append('All_HLT')
for trigger in HLTList:
    if remove_trigger(trigger):continue
    if 'All_HLT' in getTriggerString.keys(): getTriggerString['All_HLT']+='||'+trigger
    else: getTriggerString['All_HLT']=trigger

## Fill string for prescaled paths
groupList.append('All_PSed')
for trigger in HLTList:
    if remove_trigger(trigger):continue
    if int(prescaleMap[trigger][0]) <=1 : continue
    if 'All_PSed' in getTriggerString.keys(): getTriggerString['All_PSed']+='||'+trigger
    else: getTriggerString['All_PSed']=trigger

## Fill string for type
if triggersTypeMap:
    groupList.append('type_signal')
    for trigger in triggersTypeMap:
        if remove_trigger(trigger):continue
        if (not ('signal' in triggersTypeMap[trigger])) and (not ('backup' in triggersTypeMap[trigger])):continue
        if 'type_signal' in getTriggerString.keys(): getTriggerString['type_signal']+='||'+trigger
        else: getTriggerString['type_signal']=trigger
    
    groupList.append('type_control')
    for trigger in triggersTypeMap:
        if remove_trigger(trigger):continue
        if not ('control' in triggersTypeMap[trigger]):continue
        if 'type_control' in getTriggerString.keys(): getTriggerString['type_control']+='||'+trigger
        else: getTriggerString['type_control']=trigger

#groupList.append('type_backup')
#for trigger in triggersTypeMap:
#    if not ('backup' in triggersTypeMap[trigger]):continue
#    if 'type_backup' in getTriggerString.keys(): getTriggerString['type_backup']+='||'+trigger
#    else: getTriggerString['type_backup']=trigger

for dataset1 in primaryDatasetList:
    for dataset2 in primaryDatasetList:
        #print str((dataset1,dataset2))
        corelation_datasetList.append((dataset1,dataset2))
        getTriggerString[(dataset1,dataset2)]='0'

for trigger in triggerList:
    for dataset in primaryDatasetList:
        corelation_trigger_datasetList.append((trigger,dataset))
        getTriggerString[(trigger,dataset)]='0'

print groupList
#print primaryDatasetList
#print pure_primaryDatasetList
#print streamList
#print pure_streamList
#print corelation_trigger_datasetList
