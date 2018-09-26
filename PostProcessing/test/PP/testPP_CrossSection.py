import argparse
import numpy as np
import ROOT

from array import array

try:
    RDataFrame = ROOT.ROOT.RDataFrame
except AttributeError:
    RDataFrame = ROOT.ROOT.Experimental.TDataFrame
     
        
SPLICES = {
    'inclusive' : dict(),
    'YB01_YS01' : dict(jet12yboost=(0, 1), jet12ystar=(0, 1)),
    'YB01_YS12' : dict(jet12yboost=(0, 1), jet12ystar=(1, 2)),
    'YB01_YS23' : dict(jet12yboost=(0, 1), jet12ystar=(2, 3)),
    'YB12_YS01' : dict(jet12yboost=(1, 2), jet12ystar=(0, 1)),
    'YB12_YS12' : dict(jet12yboost=(1, 2), jet12ystar=(1, 2)),
    'YB23_YS01' : dict(jet12yboost=(2, 3), jet12ystar=(0, 1)),
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
        .Define("isValid", "(jet1HLTAssignedPathEfficiency>0.0)")
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
            _splice_dfs[_splice_name] = _splice_dfs[_splice_name].Filter("{lo}<={var}&&{var}<{hi}".format(lo=_bin_spec[0], hi=_bin_spec[1], var=_var))

    # -- create histograms
    for _splice_name, _splice_df in _splice_dfs.iteritems():
        for _var in ('jet12mass', 'jet12ptave', 'jet1pt'):
            for _w in (None, "totalWeight", 'triggerEfficiencyWeight', 'triggerPrescaleWeight'):
                _hist_name = '_'.join([_s for _s in (_var, _w) if _s is not None])
                _hist_name_withsplice = '_'.join([_s for _s in (_var, _w, _splice_name) if _s is not None])
                _binning = BINNINGS[_var]
                _hist_model = ROOT.RDF.TH1DModel(_hist_name, _hist_name_withsplice, len(_binning)-1, array('f', _binning))
                if _w is None:
                    _hs[_splice_name][_hist_name] = _splice_df.Histo1D(_hist_model, _var)
                else:
                    _hs[_splice_name][_hist_name] = _splice_df.Histo1D(_hist_model, _var, _w)

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

