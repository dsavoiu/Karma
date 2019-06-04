from __future__ import print_function

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
            print("[INFO] Task '{}' has not yet been run...")
        else:
            print("[INFO] Task '{}' took {} ({} seconds)".format(self._name, self.get_duration_string(), round(self._duration, 3)))


class PostProcessor(object):

    class ObjectType(Enum):
        histogram = 1
        profile = 2

    def __init__(self, data_frame, splitting_spec, quantities):
        self._df_bare = data_frame
        self._splitting_spec = splitting_spec
        self._qs = quantities

        self._specs = []

    @staticmethod
    def _get_directory_from_split_name(split_name):
        '''split name "key1:value1/key2:value2/key3:value3" -> path "value1/value2/value3"'''
        _path_elements = split_name.split('/')
        # remove splitting keys from path
        _path_elements = [_pe.split(':', 1)[-1] for _pe in _path_elements]
        return '/'.join(_path_elements)

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

    def _get_quantity_binning(self, quantity_name, split_dict):
        '''retrieve the binning for a quantity, taking named binnings into consideration.'''
        # check if a (unique) custom binning has been defined for this quantity for this splitting
        _binning = None
        if self._qs[quantity_name].named_binning_keys:
            _keys_with_named_binnings = set(self._qs[quantity_name].named_binning_keys).intersection(split_dict.keys())
            if _keys_with_named_binnings:
                if len(_keys_with_named_binnings) > 1:
                    raise ValueError("Quantity '{}' returned more than one match for named binning keys: {}".format(quantity_name, _keys_with_named_binnings))
                _named_binning_key = list(_keys_with_named_binnings)[0]
                _binning = self._qs[quantity_name].get_named_binning(_named_binning_key, split_dict[_named_binning_key])
                if _binning is None:
                    print(
                        "[WARNING] Splitting-dependent binning for quantity '{}' and splitting key "
                        "'{}' is defined, but not for splitting value '{}'! "
                        "Will use default binning.".format(quantity_name, _named_binning_key, split_dict[_named_binning_key])
                    )
        # if no named binning was found, use default binning
        if _binning is not None:
            return _binning
        else:
            return self._qs[quantity_name].binning

    def _create_objects(self):
        # -- create quantity shape histograms for each split
        self._root_objects = {}  # keys are paths of the form 'splitting_key1:splitting_value1/.../splitting_keyN:splitting_valueN'

        for _split_name, _split_df in self._split_dfs.iteritems():
            self._root_objects[_split_name] = {}

            _split_dict = dict([_path_element.split(':', 1) for _path_element in _split_name.split('/')])

            for _obj_type, _vars_xyz, _weight in self._specs:
                _var_x, _var_y, _var_z = _vars_xyz

                _var_string_for_title = '_'.join([_v for _v in _vars_xyz if _v is not None])
                _name_suffix = '_'.join([_s for _s in (_var_x, _weight) if _s is not None])
                _title = '_'.join([_s for _s in (_var_string_for_title, _weight, _split_name) if _s is not None])

                # -- determing binnings in 'x' (and 'y' and 'z', if specified)

                _x_binning = self._get_quantity_binning(quantity_name=_var_x, split_dict=_split_dict)

                if _var_z is not None:
                    # Case 1: var 'z' specified -> 3D histogram/2D profile requested
                    assert(_var_y is not None)  # cannot have 'z' without 'y'
                    _y_binning = self._get_quantity_binning(quantity_name=_var_y, split_dict=_split_dict)
                    _z_binning = self._get_quantity_binning(quantity_name=_var_z, split_dict=_split_dict)

                    _var_z_subdict = self._root_objects[_split_name].setdefault(_var_z, {})  # ensure '_var_z' subdict exists
                    _var_y_subdict = _var_z_subdict.setdefault(_var_y, {})  # ensure '_var_y' subdict exists
                elif _var_y is not None:
                    # Case 2: no var 'z' specified, but var 'y' specified -> 2D histogram/profile requested
                    _y_binning = self._get_quantity_binning(quantity_name=_var_y, split_dict=_split_dict)
                    _var_y_subdict = self._root_objects[_split_name].setdefault(_var_y, {})  # ensure '_var_y' subdict exists

                if _obj_type == self.__class__.ObjectType.histogram:
                    if _var_z is not None:
                        # implied -> _var_y is also not `None`
                        _obj_name = 'h3d_' + _name_suffix
                        _obj_model = ROOT.RDF.TH3DModel(_obj_name, _title,
                            len(_x_binning)-1, array('f', _x_binning),
                            len(_y_binning)-1, array('f', _y_binning),
                            len(_z_binning)-1, array('f', _z_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_var_z][_var_y][_obj_name] = _split_df.Histo3D(_obj_model, _var_x, _var_y, _var_z)
                        else:
                            self._root_objects[_split_name][_var_z][_var_y][_obj_name] = _split_df.Histo3D(_obj_model, _var_x, _var_y, _var_z, _weight)
                    elif _var_y is not None:
                        _obj_name = 'h2d_' + _name_suffix
                        _obj_model = ROOT.RDF.TH2DModel(_obj_name, _title,
                            len(_x_binning)-1, array('f', _x_binning),
                            len(_y_binning)-1, array('f', _y_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Histo2D(_obj_model, _var_x, _var_y)
                        else:
                            self._root_objects[_split_name][_var_y][_obj_name] = _split_df.Histo2D(_obj_model, _var_x, _var_y, _weight)
                    else:
                        _obj_name = 'h_' + _name_suffix
                        _obj_model = ROOT.RDF.TH1DModel(_obj_name, _title,
                            len(_x_binning)-1, array('f', _x_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_obj_name] = _split_df.Histo1D(_obj_model, _var_x)
                        else:
                            self._root_objects[_split_name][_obj_name] = _split_df.Histo1D(_obj_model, _var_x, _weight)

                elif _obj_type == self.__class__.ObjectType.profile:
                    assert _var_y is not None
                    if _var_z is not None:
                        _obj_name = 'p2d_' + _name_suffix
                        _obj_model = ROOT.RDF.TProfile2DModel(_obj_name, _title,
                            len(_x_binning)-1, array('f', _x_binning),
                            len(_y_binning)-1, array('f', _y_binning))
                        if _weight is None:
                            self._root_objects[_split_name][_var_z][_var_y][_obj_name] = _split_df.Profile2D(_obj_model, _var_x, _var_y, _var_z)
                        else:
                            self._root_objects[_split_name][_var_z][_var_y][_obj_name] = _split_df.Profile2D(_obj_model, _var_x, _var_y, _var_z, _weight)
                    else:
                        _obj_name = 'p_' + _name_suffix
                        _obj_model = ROOT.RDF.TProfile1DModel(_obj_name, _title,
                            len(_x_binning)-1, array('f', _x_binning))
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
                try:
                    # x, y *and* z provided
                    _x, _y, _z = _hspec.split(':', 2)
                except ValueError:
                    # only x and y provided -> set 'z' to None
                    _x, _y, _z = _hspec.split(':', 1) + [None]
            else:
                _x, _y, _z = (_hspec, None, None)

            self._specs.append((self.__class__.ObjectType.histogram, (_x, _y, _z), _weight_spec))

    def add_profiles(self, profile_specs):
        for _pspec in profile_specs:
            # determine weights
            _weight_spec = None
            if '@' in _pspec:
                _pspec, _weight_spec = _pspec.split('@', 1)

            # determine xy pairs
            assert ':' in _pspec
            try:
                # x, y *and* z provided
                _x, _y, _z = _pspec.split(':', 2)
            except ValueError:
                # only x and y provided -> set 'z' to None
                _x, _y, _z = _pspec.split(':', 1) + [None]

            self._specs.append((self.__class__.ObjectType.profile, (_x, _y, _z), _weight_spec))

    @staticmethod
    def _write_output_recursively(object_or_dict, output_file, output_path):
        '''write `object_or_dict` to path `output_path` if ROOT object or call recursively for all subobjects'''

        # write out ROOT objects
        if isinstance(object_or_dict, dict):
            # create the output directory inside the ROOT file (if it does not exist)
            if not output_file.GetDirectory(output_path):
                output_file.mkdir(output_path)
            # recurse through all the subdictionaries
            for _subkey, _subobject_or_dict in object_or_dict.iteritems():
                _subdir = "{}/{}".format(output_path, _subkey)
                PostProcessor._write_output_recursively(_subobject_or_dict, output_file, _subdir)
        else:
            # write out the ROOT objects to the output directory
            _output_dir = '/'.join(output_path.split('/')[:-1])
            if _output_dir:
                output_file.cd(_output_dir)
            object_or_dict.Write()

    def run(self, output_file_path):

        if not self._specs:
            print("[WARNING] No histograms and/or profiles booked for output. No file written.")
            return

        self._split_df()
        self._create_objects()

        _outfile = ROOT.TFile(output_file_path, "RECREATE")
        _split_names = set(self._root_objects.keys())

        for _split_name in sorted(_split_names):
            _directory_path = self._get_directory_from_split_name(_split_name)
            _object_or_dict = self._root_objects.get(_split_name, {})

            PostProcessor._write_output_recursively(_object_or_dict, _outfile, _directory_path)

        _outfile.Close()

