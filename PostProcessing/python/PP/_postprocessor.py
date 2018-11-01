import argparse
import numpy as np
import os
import ROOT
import time

from array import array
from enum import Enum


__all__ = ["PostProcessor", "Timer"]


class Timer:
    def __init__(self, name):
        self._name = name
        self._start = None
        self._end = None
        self._duration = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, *args):
        self._end = time.time()
        self._duration = self._end - self._start

    def get_duration_string(self):
        if self._duration is None:
            return "<not run>"
        else:
            _remaining_duration = self._duration
            _s = []
            for (_unit_name, _unit_length_in_seconds) in zip(['hours', 'minutes'], [3600, 60]):
                _duration_in_units = int(_remaining_duration)/int(_unit_length_in_seconds)
                _s.append("{} {}".format(_duration_in_units, _unit_name))
                _remaining_duration -= _duration_in_units * _unit_length_in_seconds
            _s.append("{} seconds".format(int(_remaining_duration)))
            _s = ", ".join(_s)
            return _s

    def report(self):
        if self._duration is None:
            print "[INFO] Task '{}' has not yet been run..."
        else:
            print "[INFO] Task '{}' took {} ({} seconds)".format(self._name, self.get_duration_string(), round(self._duration, 3))


class PostProcessor(object):

    class ObjectType(Enum):
        histogram = 1
        profile = 2

    def __init__(self, data_frame, splitting_spec, quantities):
        self._df_bare = data_frame
        self._splitting_spec = splitting_spec
        self._qs = quantities

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

                _x_binning = self._qs[_var_x].binning  # TODO: raise if no quantity `_var_x`?
                _y_binning = None
                if _var_y is not None:
                    self._root_objects[_split_name].setdefault(_var_y, {})  # ensure '_var_y' subdict exists
                    _y_binning = self._qs[_var_y].binning  # TODO: raise if no quantity `_var_y`?

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


