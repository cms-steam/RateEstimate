#!/bin/bash

MYDIR=/afs/cern.ch/user/v/vannerom/work/cms-steam/RateEstimate/
CMSSWDir=/afs/cern.ch/user/v/vannerom/work/CMSSW_7_6_3_patch2/src/
#FILES=root://eoscms//eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Spring15/Hui_HLTRates_2e33_25ns_V4p4_V1/*
FILES=/afs/cern.ch/user/v/vannerom/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Spring15/Hui_HLTRates_2e33_25ns_V4p4_V1/*

for f in $FILES
do
fbase=$( basename "$f" )
#fbase="HLTPhysics1"
echo $fbase
#  echo "Processing $fbase file..."
for i in `seq 1 350`
do
  echo ${i}

       (                                                                                                                                       
      cat <<EOF                                                                                                                                     
curr_dir=`pwd`                                                                                                                                                                                                                                
cd ${MYDIR}
source env.sh
python RateEstimate.py -n $i -d $fbase
EOF
) > submit_${fbase}_${i}.job


chmod +x submit_${fbase}_${i}.job 
#myfile=submit_$i.job  
#bsub -q 8nh submit_${fbase}_${i}.job #myfile
bsub -q 8nh -eo err.dat -oo out.dat submit_${fbase}_${i}.job
#bsub -q 8nh -eo err.dat -oo out.dat -J "myjob"$str2 "python RateEstimate.py -n $i"
done
done

#cd ${CMSSWDir} 
#eval `scramv1 runtime -sh`
#cd -
#source /cvmfs/cms.cern.ch/slc6_amd64_gcc491/lcg/root/6.02.10/bin/thisroot.sh
