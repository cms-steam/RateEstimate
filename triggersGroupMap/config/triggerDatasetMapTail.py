triggersToRemove = [
    ## not in stream A
    'HLT_EcalCalibration_v',
    
    # use UTCA (not simulated in MC)
    'HLT_HcalUTCA_v',
    
    # use NZS (not simulated in MC)
    'HLT_HcalPhiSym_v',
    'HLT_HcalNZS_v',
    
    # fake triggers
    'HLT_BCToEFilter_v',
    'HLT_RemovePileUpDominatedEventsGen_v',
    'HLT_RemovePileUpDominatedEvents_v',
    'HLT_EmFilter_v',
    'HLT_EmGlobalFilter_v',
    'HLT_MuFilter_v',
    'HLT_MuFilterTP_v',

    # trigger without L1 seeds
    'HLT_Random_v',
    'HLT_Physics_v',
]

triggersToRemoveFromTotalRate = [
    # PPD triggers
#    'HLT_HT2000_v',
#    'HLT_HT2500_v',
#    'HLT_MET250_v',
#    'HLT_MET300_v',
#    'HLT_MET600_v',
#    'HLT_MET700_v',
#    'HLT_Mu350_v',
#    'HLT_PFMET300_v',
#    'HLT_PFMET400_v',
#    'HLT_PFMET500_v',
#    'HLT_PFMET600_v',
#    'HLT_Photon500_v',
#    'HLT_Photon600_v',
]

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
    for group in triggersGroupMap[trigger]:
        if not group in groupList: groupList.append(group)
    for dataset in triggersDatasetMap[trigger]:
        if not dataset in primaryDatasetList: primaryDatasetList.append(dataset)

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
    for group in triggersGroupMap[trigger]:
        if group in getTriggerString.keys(): getTriggerString[group]+='||'+trigger
        else: getTriggerString[group]=trigger

## Fill twoGroupsList and getTriggerString
#for group1 in groupList:
#    for group2 in groupList:
#        if (not group1.isdigit()) and (not group2.isdigit()): twoGroups = group1 + "-" + group2
#        if not (twoGroups in twoGroupsList) and ("L1" not in twoGroups):
#            twoGroupsList.append(twoGroups)
#            twoGroupsTrigger="("+(getTriggerString[group1])+")&&("+(getTriggerString[group2])+")"
#            getTriggerString[twoGroups]=twoGroupsTrigger

### Fill twoHLTsList and getTriggerString
#for trigger1 in HLTList:
#    for trigger2 in HLTList:
#        twoHLTs = trigger1 + "-" + trigger2
#        if not (twoHLTs in twoHLTsList):
#            twoHLTsList.append(twoHLTs)
#            twoHLTsTrigger="("+(getTriggerString[trigger1])+")&&("+(getTriggerString[trigger2])+")"
#            getTriggerString[twoHLTs]=twoHLTsTrigger

## Fill string for All group

groupList.append('All_HLT_paths')
groupList.append('All_HLT_aliases')

i = 0
for trigger in HLTList:
    if (trigger in triggersToRemoveFromTotalRate) or (trigger in triggersToRemove): continue
    if 'All_HLT_aliases' in getTriggerString.keys(): getTriggerString['All_HLT_aliases']+='||HLT_'+str(i)
    else: getTriggerString['All_HLT_aliases']='HLT_0'
    i += 1

for trigger in HLTList:
    if (trigger in triggersToRemoveFromTotalRate) or (trigger in triggersToRemove): continue
    if 'All_HLT_paths' in getTriggerString.keys(): getTriggerString['All_HLT_paths']+='||'+trigger
    else: getTriggerString['All_HLT_paths']=trigger
