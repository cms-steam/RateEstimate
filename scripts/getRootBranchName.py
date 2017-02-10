import ROOT
import os

#rootfile_dir = '/afs/cern.ch/user/x/xgao/eos/cms/store/group/dpg_trigger/comm_trigger/TriggerStudiesGroup/STEAM/Run2016E/HLTPhysics_2016E/HLTPhysics/HLTPhysics0/160726_112922/0000'
#if '.root' in rootfile_dir:
#    tmp_file = ROOT.TFile.Open(rootfile_dir)
#    print 'open file : %s'%rootfile_dir
#else:
#    for filename in os.listdir(rootfile_dir):
#        if 'root' in filename:
#            tmp_file = ROOT.TFile.Open(rootfile_dir+'/'+filename)
#            print 'open file : %s'%filename
#            break
#
tmp_file = ROOT.TFile.Open('hltbits_1.root')
tree = ROOT.gDirectory.Get('HltTree')
for leaf in tree.GetListOfLeaves():
    name = leaf.GetName()
    print name

