import argparse
import numpy as np
import ROOT

from array import array

try:
    RDataFrame = ROOT.ROOT.RDataFrame
except AttributeError:
    RDataFrame = ROOT.ROOT.Experimental.TDataFrame
     
SPLICES = {
    'all' : dict(),
    'HLT_PFJet40' : dict(jet1HLTAssignedPathIndex=0),
    'HLT_PFJet60' : dict(jet1HLTAssignedPathIndex=1),
    'HLT_PFJet80' : dict(jet1HLTAssignedPathIndex=2),
    'HLT_PFJet140' : dict(jet1HLTAssignedPathIndex=3),
    'HLT_PFJet200' : dict(jet1HLTAssignedPathIndex=4),
    'HLT_PFJet260' : dict(jet1HLTAssignedPathIndex=5),
    'HLT_PFJet320' : dict(jet1HLTAssignedPathIndex=6),
    'HLT_PFJet400' : dict(jet1HLTAssignedPathIndex=7),
    'HLT_PFJet450' : dict(jet1HLTAssignedPathIndex=8),
    'HLT_PFJet500' : dict(jet1HLTAssignedPathIndex=9),
}

BINNINGS = {
    'jet12mass' : np.linspace(0, 8000, 101),
    'jet1pt' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    'jet12ptave' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
}

if __name__ == "__main__":

    p = argparse.ArgumentParser()
    
    p.add_argument('FILE', help="File containing flat ntuple")
    p.add_argument('-t', '--tree', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
    p.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
    p.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
    p.add_argument('-o', '--output-file', help="Name of file to write output to (default: 'testPP_CrossSection_py_out.root')", default="testPP_CrossSection_py_out.root")
    
    args = p.parse_args()

    #_file = "/storage/c/dsavoiu/dijet_results/DijetAna_JetHT_Legacy-07Aug2017-v1_2018-08-10/merged_flat.root"

    if args.jobs > 1:
        ROOT.ROOT.EnableImplicitMT(int(args.jobs));
    _df_bare = RDataFrame(args.tree, args.FILE)

    _df = (_df_bare
        .Define("isValid", "((jet1HLTAssignedPathEfficiency>0.0)&&(jet1HLTAssignedPathIndex>=0))")
        .Define("metOverSumET", "met/sumEt")
        .Filter("isValid")
        .Filter("abs(jet1pt) > 60")
        .Filter("abs(jet2pt) > 60")
        .Filter("abs(jet1y) < 3.0")
        .Filter("abs(jet2y) < 3.0")
        .Define("totalWeight", "jet1HLTAssignedPathPrescale/jet1HLTAssignedPathEfficiency")
        .Define("triggerEfficiencyWeight", "1.0/jet1HLTAssignedPathEfficiency")
        .Define("triggerPrescaleWeight", "jet1HLTAssignedPathPrescale"))

    if args.num_events >= 0:
        _df_bare = _df_bare.Range(0, args.num_events)

    # -- create splices
    _splice_dfs = {}
    _hs = {}
    for _splice_name, _splice_dict in SPLICES.iteritems():
        _hs[_splice_name] = dict()
        _splice_dfs[_splice_name] = _df
        for _var, _bin_spec in _splice_dict.iteritems():
            if isinstance(_bin_spec, tuple):
                _splice_dfs[_splice_name] = _splice_dfs[_splice_name].Filter("{lo}<={var}&&{var}<{hi}".format(lo=_bin_spec[0], hi=_bin_spec[1], var=_var))
            else:
                _splice_dfs[_splice_name] = _splice_dfs[_splice_name].Filter("{var}=={value}".format(value=_bin_spec, var=_var))

    # -- create histograms
    _var_y = "jet1HLTAssignedPathEfficiency"
    for _splice_name, _splice_df in _splice_dfs.iteritems():
        for _var_x in ('jet12mass', 'jet12ptave', 'jet1pt'):
            _hist_name = _var_x
            _hist_name_withsplice = '_'.join([_var_x, _splice_name])
            _binning = BINNINGS[_var_x]
            _hist_model = ROOT.RDF.TProfile1DModel(_hist_name, _hist_name_withsplice, len(_binning)-1, array('f', _binning), "")
            _hs[_splice_name][_hist_name] = _splice_df.Profile1D(_hist_model, _var_x, _var_y)

    # -- write output

    _outfile = ROOT.TFile(args.output_file, "RECREATE")

    for _splice_name, _hists_dict in sorted(_hs.iteritems()):
        _outfile.cd()
        _outfile.mkdir(_splice_name)
        _outfile.cd(_splice_name)
        for _, _h in sorted(_hists_dict.iteritems()):
            _h.Write()

    _outfile.Close()


























"""
class DataFrameHelper(object):
    def __init__(self, filename, treename, branchname):
        self._filename = filename
        self._treename = treename
        self._branchname = branchname
        self._prelude = 'auto df = ROOT::Experimental::TDataFrame("{treename}", "{filename}")'.format(treename=self._treename, filename=self._filename)
        self._histo_codelines = []
        self._splices = {}

    def define(self, q_name, q_expression=None):
        if q_expression is None:
            q_expression = "entry.{}".format(q_name)
        self._prelude += '.Define("{name}", [](const dijet::NtupleEntry& entry) {{ return {expr}; }}, {{"{branchname}"}})'.format(
            name=q_name,
            expr=q_expression,
            branchname=self._branchname
        )

    def filter(self, condition):
        self._prelude += '.Filter("{condition}")'.format(condition=condition)

    def histo1d(self, quantity, binning, weight=None):
        assert len(binning) == 3
        _binning_string = ', '.join(map(str, binning))
        _name = "{quantity}".format(quantity=quantity)
        if weight is not None:
            self._histo_codelines.append('auto h_{name}_{weight} = df.Histo1D({{"{name}_{weight}", "{name}_{weight}", {binning_string}}}, "{quantity}", "{weight}");'.format(
                name=_name,
                weight=weight,
                quantity=quantity,
                binning_string=_binning_string
            ))
        else:
            self._histo_codelines.append('auto h_{name} = df.Histo1D({{"{name}", "{name}", {binning_string}}}, "{quantity}");'.format(
                name=_name,
                quantity=quantity,
                binning_string=_binning_string
            ))

    #def add_splice(self, name):
    #    self._splices[

    def finalize(self):
        # initialize dataframe
        #ROOT.gInterpreter.Declare(self._prelude + ';')
        print self._prelude + ';'
        # initialize histograms
        for _hcl in self._histo_codelines:
            print _hcl
            #ROOT.gInterpreter.Declare(_hcl)
"""

