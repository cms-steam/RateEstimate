### This file works with both Phys14 and Fall13 samples ###

datasetList = [
'QCD_Pt-15to30_Tune4C_13TeV_pythia8',
'QCD_Pt-30to50_Tune4C_13TeV_pythia8',
'QCD_Pt-50to80_Tune4C_13TeV_pythia8',
'QCD_Pt-80to120_Tune4C_13TeV_pythia8',
'QCD_Pt-120to170_Tune4C_13TeV_pythia8',
'QCD_Pt-170to300_Tune4C_13TeV_pythia8',
'QCD_Pt-300to470_Tune4C_13TeV_pythia8',
'QCD_Pt-470to600_Tune4C_13TeV_pythia8',
'QCD_Pt-600to800_Tune4C_13TeV_pythia8',
#'QCD_Pt-800to1000_Tune4C_13TeV_pythia8',
#'QCD_Pt-1000to1400_Tune4C_13TeV_pythia8',
#'QCD_Pt-1400to1800_Tune4C_13TeV_pythia8',
#'QCD_Pt-1800_Tune4C_13TeV_pythia8',

'DYToEE_Tune4C_13TeV-pythia8',
'DYToMuMu_Tune4C_13TeV-pythia8',
'WToENu_Tune4C_13TeV-pythia8',
'WToMuNu_Tune4C_13TeV-pythia8',
]

datasetNegWeightList=[
'DYToMuMu_Tune4C_13TeV-pythia8'
]

datasetAntiMuList= [
'QCD_Pt-30to50_Tune4C_13TeV_pythia8',
'QCD_Pt-50to80_Tune4C_13TeV_pythia8',
'QCD_Pt-80to120_Tune4C_13TeV_pythia8',
]

datasetAntiEMList= [
'QCD_Pt-30to50_Tune4C_13TeV_pythia8',
'QCD_Pt-50to80_Tune4C_13TeV_pythia8',
'QCD_Pt-80to120_Tune4C_13TeV_pythia8',
'QCD_Pt-120to170_Tune4C_13TeV_pythia8',
'QCD_Pt-30to50_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
'QCD_Pt-50to80_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
'QCD_Pt-80to120_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
]

datasetEMEnrichedList = [
'QCD_Pt-30to80_EMEnriched_Tune4C_13TeV_pythia8',
'QCD_Pt-80to170_EMEnriched_Tune4C_13TeV_pythia8',
]

datasetMuEnrichedList = [
'QCD_Pt-30to50_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
'QCD_Pt-50to80_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
'QCD_Pt-80to120_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8',
]

xsectionDatasets ={
'QCD_Pt-15to30_Tune4C_13TeV_pythia8':2237000000.,
'QCD_Pt-30to50_Tune4C_13TeV_pythia8':161500000.,
'QCD_Pt-50to80_Tune4C_13TeV_pythia8':22110000.,
'QCD_Pt-80to120_Tune4C_13TeV_pythia8':3000114.3,
'QCD_Pt-120to170_Tune4C_13TeV_pythia8':493200.,
'QCD_Pt-170to300_Tune4C_13TeV_pythia8':120300.,
'QCD_Pt-300to470_Tune4C_13TeV_pythia8':7475.,
'QCD_Pt-470to600_Tune4C_13TeV_pythia8':587.1,
'QCD_Pt-600to800_Tune4C_13TeV_pythia8':167.,
'QCD_Pt-600to800_Tune4C_13TeV_pythia8':28.25,
'QCD_Pt-800to1000_Tune4C_13TeV_pythia8':8.195,
'QCD_Pt-1000to1400_Tune4C_13TeV_pythia8':0.7346,
'QCD_Pt-1800_Tune4C_13TeV_pythia8':0.1091,

'QCD_Pt-30to80_EMEnriched_Tune4C_13TeV_pythia8':185900000 * 0.06071,
'QCD_Pt-80to170_EMEnriched_Tune4C_13TeV_pythia8':3529000 * 0.15443,

'QCD_Pt-30to50_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8':164300000 * 0.01213,
'QCD_Pt-50to80_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8':21810000 * 0.02301,
'QCD_Pt-80to120_MuEnrichedPt5_PionKaonDecay_Tune4C_13TeV_pythia8':2999000 * 0.03641,

'DYToEE_Tune4C_13TeV-pythia8':6960.,
'DYToMuMu_Tune4C_13TeV-pythia8':6870.,
'WToENu_Tune4C_13TeV-pythia8':16000.,
'WToMuNu_Tune4C_13TeV-pythia8':16100.,
}
