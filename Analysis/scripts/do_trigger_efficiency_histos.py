import ROOT

from collections import OrderedDict

HLT_THRESHOLDS = [40,60,80,140,200,260,320,400,450,500]

TRIGGER_PATHS = (["HLT_PFJet{}".format(_threshold) for _threshold in HLT_THRESHOLDS])

#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/dijet_output.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-04-27_16-02/dijet_test_trigger_efficiencies.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-05-01_16-32/dijet_test_trigger_efficiencies.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-05-02_10-18/dijet_test_trigger_efficiencies_incomplete.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-05-02_10-18/dijet_test_trigger_efficiencies.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/dijet_output.root"
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-05-02_18-00/dijet_test_trigger_efficiencies.root"

## ptavg
#_filepath = "/portal/ekpbms1/home/dsavoiu/Dijet/CMSSW_8_0_29_dijetAnalysis/src/JetAnalysis/DijetAnalysis/work/test_trigger_efficiencies_2018-05-04_11-26/dijet_test_trigger_efficiencies_inc.root"
# mjj
_filepath = "DijetTE_SingleMuon_Run2016G-Legacy-07Aug2017-v1.root"

_file = ROOT.TFile(_filepath)
_pipelines = [_k.GetName() for _k in _file.GetListOfKeys() if _k.GetName().startswith('ys')]

_h_eff = OrderedDict()

_h_ref = _file.Get("Reference")
if not _h_ref:
    print "ERROR: histogram 'Reference' not found!"

for _itp, _tp in enumerate(TRIGGER_PATHS):
    _h_tp = _file.Get("{}".format(_tp))
    if not _h_tp:
        print "ERROR: histogram for path '{}' not found!".format(_tp)

    _h_eff[_tp] = ROOT.TEfficiency(_h_tp, _h_ref)


_file_out = ROOT.TFile("trigger_efficiencies.root", "RECREATE")

for _h_name, _h in _h_eff.iteritems():
    _h.Write(_h_name)

_file_out.Close()
