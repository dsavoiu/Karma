import argparse
import numpy as np
import os
import ROOT

from array import array


def split_df(data_frame, splitting_spec):
    # -- create splits
    _split_dfs = {}
    for _split_name, _split_dict in splitting_spec.iteritems():
        _split_dfs[_split_name] = data_frame
        for _var, _bin_spec in _split_dict.iteritems():
            if isinstance(_bin_spec, tuple):
                _split_dfs[_split_name] = _split_dfs[_split_name].Filter("{lo}<={var}&&{var}<{hi}".format(lo=_bin_spec[0], hi=_bin_spec[1], var=_var))
            else:
                _split_dfs[_split_name] = _split_dfs[_split_name].Filter("{var}=={value}".format(value=_bin_spec, var=_var))
    return _split_dfs


def create_histograms(split_dfs, quantity_binnings, weights=None):

    if weights is None:
        weights = [None]

    # -- create quantity shape histograms for each split
    _hs = {}
    for _split_name, _split_df in split_dfs.iteritems():
        _hs[_split_name] = {}
        for _var, _binning in quantity_binnings.iteritems():
            for _w in weights:
                _hist_name = 'h_' + '_'.join([_s for _s in (_var, _w) if _s is not None])
                _hist_name_withsplit = '_'.join([_s for _s in (_var, _w, _split_name) if _s is not None])
                _hist_model = ROOT.RDF.TH1DModel(_hist_name, _hist_name_withsplit, len(_binning)-1, array('f', _binning))
                if _w is None:
                    _hs[_split_name][_hist_name] = _split_df.Histo1D(_hist_model, _var)
                else:
                    _hs[_split_name][_hist_name] = _split_df.Histo1D(_hist_model, _var, _w)
    return _hs

def create_profiles(split_dfs, quantity_binnings, vars_y):

    # -- create profiles
    _ps = {}
    for _split_name, _split_df in split_dfs.iteritems():
        _ps[_split_name] = {}
        for _var_y in vars_y:
            _ps[_split_name][_var_y] = {}

        for _var_x, _binning in quantity_binnings.iteritems():
            for _var_y in vars_y:
                _hist_name = 'p_' + _var_x
                _hist_name_withsplit = '_'.join([_var_y, 'vs', _var_x, _split_name])
                _hist_model = ROOT.RDF.TProfile1DModel(_hist_name, _hist_name_withsplit, len(_binning)-1, array('f', _binning), "")
                _ps[_split_name][_var_y][_hist_name] = _split_df.Profile1D(_hist_model, _var_x, _var_y)
    return _ps

def write_to_file(filename, histograms={}, profiles={}):

    if not histograms and not profiles:
        print "[WARNING] No histograms and/or profiles booked for output. No file written."
        return

    _outfile = ROOT.TFile(filename, "RECREATE")

    _split_names = set(histograms.keys()).union(set(profiles.keys()))

    for _split_name in sorted(_split_names):
        _outfile.cd()

        _outfile.mkdir(_split_name)
        _outfile.cd(_split_name)

        _hists_dict = histograms.get(_split_name, {})
        for _, _h in sorted(_hists_dict.iteritems()):
            #print _split_name, _
            _h.Write()

        _profiles_dict = profiles.get(_split_name, {})
        for _var_y, _profiles_dict_var_y in sorted(_profiles_dict.iteritems()):
            _dir = "{}/{}".format(_split_name,_var_y)
            _outfile.mkdir(_dir)
            _outfile.cd(_dir)
            for _, _p in sorted(_profiles_dict_var_y.iteritems()):
                #print _split_name, _var_y, _
                _p.Write()

    _outfile.Close()


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('FILE', help="File containing flat ntuple")
    p.add_argument('SPLITTING_KEY', help="Key which identifies the set of cuts used for separating the sample into subsamples.")

    p.add_argument('-t', '--tree', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
    p.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
    p.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
    p.add_argument('-o', '--output-file', help="Name of file to write output to")

    p.add_argument('--x-quantities', help="List of quantities for which to create shapes (1D histograms).", nargs="+")
    p.add_argument('--y-quantities', help="List of quantities for which to create profiles. One profile will be created for each pair of x and y quanities.", nargs="+")
    p.add_argument('--weights', help="List of quantities to use as weights when filling shape histograms. A (separate) weighted histogram is created for each weight", nargs="+")

    p.add_argument('--overwrite', help="Overwrite output file, if it exists.", action='store_true')

    return p.parse_args()

