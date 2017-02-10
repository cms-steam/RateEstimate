import time
import datetime
import os
import shlex
import subprocess
import sys
sys.path.append("../")
from triggersGroupMap.HLT_Menu_v4p2_v6_fake import *
from datasetCrossSections.datasetCrossSectionsSummer16 import *


MYDIR=os.getcwd()
folder = '/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Spring16_FlatPU8to37/HLTRates_v4p2_V2_unPS_MC_2017jan19'

def runCommand(commandLine):
    #sys.stdout.write("%s\n" % commandLine)
    args = shlex.split(commandLine)
    retVal = subprocess.Popen(args, stdout = subprocess.PIPE)
    return retVal

def lsl(file_or_path,my_filelist):
    executable_eos = '/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
    '''
    List EOS file/directory content, returning the information found in 'eos ls -l'.
    The output is a list of dictionaries with the following entries:
        permissions
        file
        modified
        size (in bytes)
    An exception of type IOError will be raised in case file/directory does not exist.
    '''

    directory = os.path.dirname(file_or_path)
    ls_command = runCommand('%s ls -l %s' % (executable_eos, file_or_path))

    stdout, stderr = ls_command.communicate()
    #print "stdout = ", stdout
    status = ls_command.returncode
    #print "status = ", status
    if status != 0:
        raise IOError("File/path = %s does not exist !!" % file_or_path)

    retVal = []
    for line in stdout.splitlines():
        fields = line.split()
        if len(fields) < 8:
            continue
        file_info = {
            'permissions' : fields[0],
            'size' : int(fields[4]),
            'file' : fields[8]
        }
        time_stamp = " ".join(fields[5:8])
        # CV: value of field[7] may be in format "hour:minute" or "year".
        #     if number contains ":" it means that value specifies hour and minute when file/directory was created
        #      and file/directory was created this year.
        if time_stamp.find(':') != -1:
            file_info['time'] = time.strptime(
                time_stamp + " " + str(datetime.datetime.now().year),
                "%b %d %H:%M %Y")
        else:
            file_info['time'] = time.strptime(time_stamp, "%b %d %Y")
        file_info['path'] = file_or_path
        #print "file_info = " % file_info
        retVal.append(file_info)
        my_filelist.append(file_info)
        tmp_path=file_info['path']+'/'+file_info['file']
        if not '.' in tmp_path[-5:]:
            isdir=True
        else:
            isdir=False
        #print "is dir: ", isdir
        #print "file_info =", file_info
        if isdir and not 'log' in tmp_path:
            lsl(file_info['path']+'/'+file_info['file'],my_filelist)
    return



def getdatasetfilenum(dataset):
    dirpath=''
    filenames=[]
    noRootFile = True
    walking_folder = folder+"/"+dataset
    eosDirContent=[]
    try:
        lsl(walking_folder,eosDirContent)
    except:
        pass
    for key in eosDirContent:
        if (("failed" in str(key['path'])) or ("log" in str(key['file']))): continue
        if (".root" in str(key['file'])):
            filenames.append("root://eoscms//eos/cms"+str(key['path'])+'/'+str(key['file']))
            dirpath = "root://eoscms//eos/cms"+walking_folder
            noRootFile = False
#    print filenames
    return len(filenames)



def getsubdic(datasetList):
    sum1=0
    dic={}
    for dataset in datasetList:
        dic[dataset]=getdatasetfilenum(dataset)
        sum1+=dic[dataset]
        print dataset+'  ,  ',dic[dataset]
    return dic,sum1

def subpu(minPU,maxPU,datasetList,numdic,my_sum):
    try:
        tmp_dir='sub_%sto%s'%(str(minPU),str(maxPU))
        os.mkdir(tmp_dir)
    except:
        pass
    try:
        os.system('mkdir %s/sub_err'%tmp_dir)
        os.system('mkdir %s/sub_out'%tmp_dir)
        os.system('mkdir %s/sub_job'%tmp_dir)
        os.system('mkdir %s/sub_job2'%tmp_dir)
    except:
        print "err!"
        pass
    j=1
    loop_mark = 10
    tmp_text = ''
    for dataset in datasetList:
        k = 0
        pre_k = 0
        for i in range(1,numdic[dataset]+1):
            print 'PU~[%s,%s]: %s : %d/%d '%(str(minPU),str(maxPU),dataset,i,numdic[dataset])
            print 'total: %d/%d  ;  %.1f %% processed '%(j,my_sum,(100*float(j)/float(my_sum)))

            tmp_jobname="submit_%s_%s.jobb"%(dataset,str(i))
            tmp_job=open(MYDIR+'/'+tmp_dir+'/sub_job/'+tmp_jobname,'w')
            tmp_job.write("curr_dir=%s\n"%(MYDIR))
            tmp_job.write("cd %s\n"%(MYDIR))
            tmp_job.write("source env.sh\n")
            tmp_job.write("cd ../\n")
            tmp_job.write("python RateEstimate.py -n %s -d %s\n"%(str(i),dataset))
            tmp_job.write("\n")
            tmp_job.close()
            tmp_job_dir = MYDIR+'/'+tmp_dir+'/sub_job/'+tmp_jobname
            os.system("chmod +x %s"%(tmp_job_dir))
            #os.system("bsub -q 1nh -eo %s/sub_err/err_%s_%s.dat -oo %s/sub_out/out_%s_%s.dat %s"%(tmp_dir,dataset,str(i),tmp_dir,dataset,str(i),MYDIR+'/'+tmp_dir+'/sub_job/'+tmp_jobname))

            k+=1
            tmp_text = tmp_text + tmp_job_dir + "\n"
            if k % loop_mark == 0 or i == numdic[dataset]:
                Tjobsname = "sub_%s_%s_%s.jobb"%(dataset, pre_k, k)
                Tjob_dir = MYDIR+'/'+tmp_dir+'/sub_job2/'+Tjobsname
                Tjob = open(Tjob_dir,"w")
                Tjob.write("%s"%(tmp_text))
                os.system("chmod +x %s"%(Tjob_dir))
                os.system("bsub -q 1nh -eo %s/sub_err/err_%s_%s.dat -oo %s/sub_out/out_%s_%s.dat %s"%(tmp_dir,dataset,k,tmp_dir,dataset,k,Tjob_dir))
                pre_k = k
                tmp_text = ''
            j+=1


datasetList+=datasetEMEnrichedList
datasetList+=datasetMuEnrichedList

numdic,my_sum=getsubdic(datasetList)
subpu(0,100,datasetList,numdic,my_sum)
