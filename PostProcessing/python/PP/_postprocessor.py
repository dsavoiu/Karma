import argparse
import numpy as np
import os
import ROOT

from array import array
from enum import Enum


__all__ = ["PostProcessor", "parse_args"]



class PostProcessor(object):

    class ObjectType(Enum):
        histogram = 1
        profile = 2

    def __init__(self, data_frame, splitting_spec, quantity_binnings):
        self._df_bare = data_frame
        self._splitting_spec = splitting_spec
        self._quantity_binnings = quantity_binnings

        self._specs = []

    def _split_df(self):
        # -- create splits
        self._split_dfs = {}
        for _split_name, _split_dict in self._splitting_spec.iteritems():
            self._split_dfs[_split_name] = self._df_bare
            for _var, _bin_spec in _split_dict.iteritems():
                if isinstance(_bin_spec, tuple):
                    self._split_dfs[_split_name] = self._split_dfs[_split_name].Filter("{lo}<={var}&&{var}<{hi}".format(lo=_bin_spec[0], hi=_bin_spec[1], var=_var))
                else:
                    self._split_dfs[_split_name] = self._split_dfs[_split_name].Filter("{var}=={value}".format(value=_bin_spec, var=_var))

    def _create_objects(self):
        # -- create quantity shape histograms for each split
        self._root_objects = {}

        for _split_name, _split_df in self._split_dfs.iteritems():
            self._root_objects[_split_name] = {}

            for _obj_type, _var_x, _var_y, _weight in self._specs:
                _name_suffix = '_'.join([_s for _s in (_var_x, _weight) if _s is not None])
                _title = '_'.join([_s for _s in (_var_x, _var_y, _weight, _split_name) if _s is not None])

                _x_binning = self._quantity_binnings[_var_x]  # TODO: raise if no binning for `_var_x`?
                _y_binning = None
                if _var_y is not None:
                    self._root_objects[_split_name].setdefault(_var_y, {})  # ensure '_var_y' subdict exists
                    _y_binning = self._quantity_binnings[_var_y]  # TODO: raise if no binning for `_var_y`?

                if _obj_type == self.__class__.ObjectType.histogram:
                    if _var_y is None:
                        _obj_name = 'h_' + _name_suffix
                        _obj_model = ROOT.RDF.TH1DModel(_obj_name, _title, len(_x_binning)-1, array('f', _x_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_obj_name] = _split_df.Histo1D(_obj_model, _var_x)
                        else:
                            self._root_objects[_split_name][_obj_name] = _split_df.Histo1D(_obj_model, _var_x, _weight)
                    else:
                        _obj_name = 'h2d_' + _name_suffix
                        _obj_model = ROOT.RDF.TH2DModel(_obj_name, _title, len(_x_binning)-1, array('f', _x_binning), len(_y_binning)-1, array('f', _y_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Histo2D(_obj_model, _var_x, _var_y)
                        else:
                            self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Histo2D(_obj_model, _var_x, _var_y, _weight)

                elif _obj_type == self.__class__.ObjectType.profile:
                    assert _var_y is not None
                    _obj_name = 'p_' + _name_suffix
                    _obj_model = ROOT.RDF.TProfile1DModel(_obj_name, _title, len(_x_binning)-1, array('f', _x_binning))
                    if _weight is None:
                        self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Profile1D(_obj_model, _var_x, _var_y)
                    else:
                        self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Profile1D(_obj_model, _var_x, _var_y, _weight)

    def add_histograms(self, histogram_specs):
        for _hspec in histogram_specs:
            # determine weights
            _weight_spec = None
            if '@' in _hspec:
                _hspec, _weight_spec = _hspec.split('@', 1)

            # determine xy pairs
            if ':' in _hspec:
                _hspec_x, _hspec_y = _hspec.split(':', 1)
            else:
                _hspec_x, _hspec_y = _hspec, None

            self._specs.append((self.__class__.ObjectType.histogram, _hspec_x, _hspec_y, _weight_spec))

    def add_profiles(self, profile_specs):
        for _pspec in profile_specs:
            # determine weights
            _weight_spec = None
            if '@' in _pspec:
                _pspec, _weight_spec = _pspec.split('@', 1)

            # determine xy pairs
            assert ':' in _pspec
            _pspec_x, _pspec_y = _pspec.split(':', 1)

            self._specs.append((self.__class__.ObjectType.profile, _pspec_x, _pspec_y, _weight_spec))

    def run(self, output_file_path):

        if not self._specs:
            print "[WARNING] No histograms and/or profiles booked for output. No file written."
            return

        self._split_df()
        self._create_objects()

        _outfile = ROOT.TFile(output_file_path, "RECREATE")
        _split_names = set(self._root_objects.keys())

        for _split_name in sorted(_split_names):
            _outfile.cd()
            _outfile.mkdir(_split_name)

            _coda_for_split = self._root_objects.get(_split_name, {})
            for _key1, _obj_handle_or_inner_dict in sorted(_coda_for_split.iteritems()):
                if isinstance(_obj_handle_or_inner_dict, dict):
                    _dir = "{}/{}".format(_split_name, _key1)
                    _outfile.mkdir(_dir)
                    _outfile.cd(_dir)
                    for _key2, _obj_handle in sorted(_obj_handle_or_inner_dict.iteritems()):
                        _obj_handle.Write()
                else:
                    _outfile.cd(_split_name)
                    _obj_handle_or_inner_dict.Write()

        _outfile.Close()


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('FILE', help="File containing flat ntuple")
    p.add_argument('SPLITTING_KEY', help="Key which identifies the set of cuts used for separating the sample into subsamples.", nargs='+')

    p.add_argument('-t', '--tree', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
    p.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
    p.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
    p.add_argument('-o', '--output-file', help="Name of file to write output to")

    p.add_argument('--histograms', help="List of histogram specifications.", nargs="+")
    p.add_argument('--profiles', help="List of profile specifications", nargs="+")

    p.add_argument('--overwrite', help="Overwrite output file, if it exists.", action='store_true')

    return p.parse_args()

