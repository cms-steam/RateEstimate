# RateEstimate
Python script used to estimate the rate of HLT

To get steam rates, can use this script and follow the step:
1. make trigger map.
2. set RateEstimate.py.
3. submit jobs to bqueues.
4. merge banch results together and calculate rates.

1. make trigger map.
make a .py script, which will be imported into RateEstimate.py in step 2. This .py can provide group, dataset, stream, prescale information.

script: triggersGroupMap/makeTriggerMap.py
parameters: from line 1 to line 10.
	file_menu = 'HLT_Menu_v4.2_v6.tsv'			# a .tsv table include menu information, download from google doc, ask it from Nadir currently.
	file_sample = 'config/triggerDatasetMapTail.py'		# no need to modify
	file_output = 'HLT_Menu_v4p2_v6.py'			# name of output .py file
	triggerName = 'tttt'					# just a label
	column_stream = 0					# column of stream, i.e: column "A" is 0, column "AB" is 27
	column_dataset = 1
	column_trigger = 2
	column_group = 4
	column_type = -1					# these columns can be set to -1, if no related column in .tsv
	column_ps = 10


2. set RateEstimate.py

script: RateEstimate.py
	this script can read Ntuples and output fired count. This script can also be submitted to bqueues, one root file one job.
parameters: from line 1 to line 60
	from triggersGroupMap.HLT_Menu_v4p2_v6 import *				# trigger map, made in step 1
	from datasetCrossSections.datasetCrossSectionsHLTPhysics import *	# provide the name of dataset
	
	batchSplit = False		# if batch jobs and submit to bqueues, set True, recommanded.
	batchSplit = True
	looping = False			# there are two method to get fired count, tree.Draw() or looping over events. Draw() is fast but less features, looping is slow but more features, for data, looping is recommanded.
	looping = True
	
	folder = '/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Run2016H/HLTPhysics_2016H_menu4p2/HLTPhysics2016H_DB' # directory to Ntuples
	localdir = '/afs/cern.ch/user/x/xgao/eos/cms'		# in case test locally, will not use if batchSplit = True
	lumi = 1              # luminosity [s-1cm-2]		# just a label
	if (batchSplit): multiprocess = 1           # number of processes
	else: multiprocess = 1 # 8 multiprocessing disbaled for now because of incompatibilities with the way the files are accessed. Need some development.
	pileupMAX = 100			# For MC
	pileupMIN = 0			# For MC
	pileupFilter = False        	# For MC use pile-up filter?
	pileupFilterGen = False    	# For MC use pile-up filter gen or L1?
	useEMEnriched = False       	# For MC use plain QCD mu-enriched samples (Pt30to170)?
	useMuEnriched = False       	# For MC use plain QCD EM-enriched samples (Pt30to170)?
	evalL1 = False              	# For MC evaluate L1 triggers rates? code can't work for 2016 L1 rates. set False
	evalHLTpaths = True        # evaluate HLT triggers rates?
	evalHLTgroups = True       # evaluate HLT triggers groups rates and global HLT and L1 rates
	evalHLTprimaryDatasets = True # evaluate HLT triggers primary datasets rates and global HLT and L1 rates
	evalHLTprimaryDatasets_core = True # evaluate HLT triggers primary datasets rates and global HLT and L1 rates
	evalHLTTrigger_primaryDatasets_core = True # evaluate HLT triggers primary datasets rates and global HLT and L1 rates
	evalHLTstream = True # evaluate HLT triggers primary datasets rates and global HLT and L1 rates
	#evalHLTtwopaths = True    # evaluate the coreelation among the HLT trigger paths rates?
	evalHLTtwogroups = False   # evaluate the coreelation among the HLT trigger groups rates?
	evalPureRate_Group = True
	evalPureRate_Dataset = True
	evalPureRate_Stream = True
	evalExclusive_Trigger = True
	evalExclusive_group = True
	evalExclusive_dataset = False
	evalExclusive_dataset = False
	use_json = True			# if use json to filter event
	json_file_name = '/afs/cern.ch/user/x/xgao/work/RateEstimate_31_08_2016/test_4.2/1p15/columns_2016H/columns_1p15e34.txt'
	label = "test"         		# a label
	runNo = "0"           		# if runNo='0' and use_json = False, means code will run for all Run. 
	LS_min = '0'			# default is 0
	LS_max = '9999'            	# default is 9999
	
	isData = True



3. submit jobs to bqueues.

script: scripts/RatesBatchScript.py
	this script can scan Ntuples directory, create job script for each root file and submit them to bqueues 8nh.
parameters: from line 8 to line 12
	note that the modules and Ntuples directory have to be same as one in RateEstimate.py

4. merge banch results together and calculate rates.

script: scripts/mergeRates_path_v2.py
    this script for individual trigger
	from triggersGroupMap.HLT_Menu_v4p2_v6 import *				# should be same in RateEstimate.py	
	from datasetCrossSections.datasetCrossSectionsHLTPhysics import * 	# should be same in RateEstimate.py
	
	Method = 1 #0: rate = count ; 1:HLT, rate = psNorm*count / LS*nLS ; 2:Zerobias, rate = 11245Hz * target nBunchs * nCount/total Event
	LS = 23.31
	PsNorm = 107*4.i	# prescale of dataset
	nLS = 246-43+1		
	nLS = 0			# recommand set 0, then code will calculate how many lumi section has been run over during read ntuples automatically.
	ps_const = 11245.0*2200.0

script: scripts/mergeRates_GroupDataset_v2.py
        this script for group, dataset, stream
