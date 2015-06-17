triggersToRemove = [
    # low pileup menu
    'HLT_FullTrack12_v',
    'HLT_FullTrack20_v',
    'HLT_FullTrack30_v',
    'HLT_FullTrack50_v',

    'HLT_PixelTracks_Multiplicity60_v',
    'HLT_PixelTracks_Multiplicity85_v',
    'HLT_PixelTracks_Multiplicity110_v',
    'HLT_PixelTracks_Multiplicity135_v',
    'HLT_PixelTracks_Multiplicity160_v',

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

triggersGroupMap = dict(triggersGroupMap.items() + triggersL1GroupMap.items())

triggerList = []
L1List = []
HLTList = []
#twoHLTsList = []
groupList = []
twoGroupsList = []
getTriggerString = {}

## Fill triggerList and groupList
for trigger in triggersGroupMap.keys():
    if trigger[:-1] in triggersToRemove: continue
    if not (trigger in triggerList) : triggerList.append(trigger)
    for group in triggersGroupMap[trigger]:
        if not (group in groupList) : groupList.append(group)

## Fill HLTList and L1List
for trigger in triggerList:
    if "HLT_" in trigger: HLTList.append(trigger)
    elif "L1_" in trigger: L1List.append(trigger)

## Fill getTriggerString get a map from trigger and group names to strings
for trigger in triggerList:
    getTriggerString[trigger]=trigger
    for group in triggersGroupMap[trigger]:
        if group in getTriggerString.keys(): getTriggerString[group]+='||'+trigger
        else: getTriggerString[group]=trigger

## Fill twoGroupsList and getTriggerString
for group1 in groupList:
    for group2 in groupList:
        twoGroups = group1 + "-" + group2
        if not (twoGroups in twoGroupsList):
            twoGroupsList.append(twoGroups)
            twoGroupsTrigger="("+(getTriggerString[group1])+")&&("+(getTriggerString[group2])+")"
            getTriggerString[twoGroups]=twoGroupsTrigger

### Fill twoHLTsList and getTriggerString
#for trigger1 in HLTList:
#    for trigger2 in HLTList:
#        twoHLTs = trigger1 + "-" + trigger2
#        if not (twoHLTs in twoHLTsList):
#            twoHLTsList.append(twoHLTs)
#            twoHLTsTrigger="("+(getTriggerString[trigger1])+")&&("+(getTriggerString[trigger2])+")"
#            getTriggerString[twoHLTs]=twoHLTsTrigger
