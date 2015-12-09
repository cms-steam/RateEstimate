#!/bin/bash

MYDIR=/afs/cern.ch/user/v/vannerom/work/test/RateEstimate/

for i in `seq 0 88`
do
#if [ "$i" -eq "17" ] || [ "$i" -eq "27" ] || [ "$i" -eq "33" ] || [ "$i" -eq "42" ] || [ "$i" -eq "44" ] || [ "$i" -eq "47" ] || [ "$i" -eq "50" ] || [ "$i" -eq "53" ] || 
#if [ "$i" -eq "30" ] || [ "$i" -eq "72" ] || [ "$i" -eq "83" ] || [ "$i" -eq "84" ]
#then 
       echo ${i}
#       str2=$(printf $i)

       (                                                                                                                                       
       cat <<EOF                                                                                                                                     
curr_dir=`pwd`                                                                                                                                                                                                       
cd ${MYDIR}                                                                                                                                     
source /afs/cern.ch/project/eos/installation/cms/etc/setup.sh 
eosmount /afs/cern.ch/user/v/vannerom/eos                                                                                                                                  
source env.sh                                                                                                                                   
python RateEstimateBatch.py -n $i
EOF
) > submit_${i}.job


chmod +x submit_${i}.job 
#myfile=submit_$i.job  
bsub -q 8nh submit_${i}.job #myfile
#bsub -q 8nh -eo err.dat -oo out.dat -J "myjob"$str2 "python RateEstimate.py -n $i"
#fi
done
