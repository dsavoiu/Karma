#!/usr/bin/env python
"""
Takes two (or more) ROOT files as an input and compares
their content (including bin-by-bin differences/ratios
of histograms and profiles, or statistics thereof)
"""
import numpy as np
import os
import sys
import yaml

from argparse import ArgumentParser
from functools import reduce

from rootpy import asrootpy
from rootpy.io import root_open

def _try_method(f, *args, **kwargs):
    '''try to run a method on an object. return result if succesful, else return the error.'''
    try:
        getattr(f, method)(*args, **kwargs)
    except Exception as e:
        return e


FEATURE_EXTRACTORS_HIST = {
    #'n_cells': lambda f: f.GetNcells(),
    #
    #'n_bins_x': lambda f: f.GetNbinsX(),
    #'n_bins_y': lambda f: f.GetNbinsY(),
    #'n_bins_z': lambda f: f.GetNbinsZ(),
    #
    #'bin_low_edge': lambda f: [b.x.low for b in asrootpy(f)[1:-1]],
    #'bin_high_edges': lambda f: [b.x.high for b in asrootpy(f)[1:-1]],
    'bin_contents': lambda f: [b.value for b in asrootpy(f)[1:-1]],
    #'bin_nonzero_contents': lambda f: [bool(b.value) for b in asrootpy(f)[1:-1]],
    #'bin_errors': lambda f: [b.error for b in asrootpy(f)[1:-1]],
    #'bin_percent': lambda f: [b.error/abs(b.value)*100 if abs(b.value) > 0 else np.nan for b in asrootpy(f)[1:-1]],
}

REDUCERS = {
    'min':     lambda a: list(np.min(a, axis=0)),
    'max'    : lambda a: list(np.max(a, axis=0)),
    'average': lambda a: list(np.mean(a, axis=0)),
    #'unique':  lambda a: list(set(a)),
    #'n_diff':  lambda a: len(set(a)),
    'n_none':  lambda a: sum(v is None for v in a),
}

def _diff(tobjects, labels, feature_extractors):
    _none_count = sum(tobject is None for tobject in tobjects)
    
    # if all inputs are `None`
    if _none_count == len(tobjects):
        return None

    if len(tobjects) == 2:
        _diff = {
            _fl_name : {
                'object_values': list(_fl(_tobject) for _tobject in tobjects),
                #'intersection': set(_fl(_tobject) for _tobject in tobjects),
            }
            for _fl_name, _fl in feature_extractors.items()
        }
        #for _fl_name in feature_extractors:
        #    _diff.update({
        #        _fl_name : {
        #            'object_value_setdiff': _diff.update[_fl_name]['object_values'].difference(_diff.update[_fl_name]['intersection'])
        #        }
        #    })
        return _diff

    else:
        raise NotImplementedError

def _serialize(tobject, feature_extractors=FEATURE_EXTRACTORS_HIST):
    return {
        _fl_name: _fl(tobject)
        for _fl_name, _fl in feature_extractors.items()
    }

def _reduce(values, reducers=REDUCERS):
    return {
        _rn : _r(values)
        for _rn, _r in reducers.items()
    }

def _extract_structure(root_file, structure_dict):
    _n_files = structure_dict['_n_files'] = structure_dict.setdefault('_n_files', 0) + 1
    _struct = structure_dict.setdefault('_root', {})
    _n_insert_missing = _n_files - 1
    _list_dicts_check_length = []
    for path, dirs, objects in root_file.walk():
            _cdir = _struct
            for _p in path.split('/'):
                if _p:
                    _cdir = _cdir.setdefault('_dirs', {})
                    _cdir = _cdir.setdefault(_p, {})

            #_cdir['_path'] = path
            #_cdir.setdefault('_dirs', [set()] * _n_insert_missing).append(set(dirs))

            _objects_dict = _cdir.setdefault('_objects', {})
            for _obj_name in objects:
                _obj = _serialize(root_file.Get(path+'/'+_obj_name))
                _obj_features = _objects_dict.setdefault(_obj_name, {}).setdefault('_features', {})
                for _feature, _value in _obj.items():
                    _list_dicts_check_length.append(_obj_features)
                    _obj_features.setdefault(_feature, [None] * _n_insert_missing).append(_value)
            #_cdir.setdefault('_objects', [dict()] * _n_insert_missing).append(_serialize(_obj))

            #_full_obj_paths = [os.path.join(path, _obj) for _obj in objects]
            #_full_dir_paths = [os.path.join(path, _dir) for _dir in dirs]

            #_objects = [root_file.Get(_obj_path) for _obj_path in _full_obj_paths]
            #_objects = [root_file.Get(_obj_path) for _obj_path in _full_obj_paths]
            #_full_dir_paths = [os.path.join(path, _dir) for _dir in dirs]

            #for _full_path in _full_dir_paths:
            #    _diff_dirs = _diff([_f2.Get(_full_path) for _f2 in [_f] + _other_files], list(range(len(_files))), feature_extractors=dict(name=lambda obj: obj.GetName()))
            #    _cdir['_dirs'] = _diff_dirs

            #for _full_path in _full_obj_paths:
            #    _diff_objects = _diff([_f2.Get(_full_path) for _f2 in [_f] + _other_files], list(range(len(_files))), feature_extractors=FEATURE_EXTRACTORS_HIST)
            #    _cdir['_objects'] = _diff_dirs

            #for _f2 in _other_files:
            #    _f2_dirs = _diff([_f2.Get(_full_path) for _full_path in _full_dir_paths], dirs, feature_extractors=dict(name=lambda obj: obj.GetName()))
            #    #_f2_objects = _diff([_f2.Get(_full_path) for _full_path in _full_obj_paths], objects, feature_extractors=FEATURE_EXTRACTORS_HIST)
            #try:
            #    _f2.close()
            #    _f2
    return structure_dict, _list_dicts_check_length

def _complete_list(n_files, list_dicts_check_length):

    for _dict in _list_dicts_check_length:
        for _feature, _value in _dict.items():
            print(n_files-len(_value))
            _dict[_feature].extend([None]*(n_files-len(_value)))
            #print(_feature, _value)

RESERVED_KEYWORDS = ('_dirs', '_objects', '_features')

def _evaluate_structure(structure_dict, ctx=None):
    if ctx is None:
        ctx = dict(n_files=structure_dict['_n_files'], path=[], in_namespace=None)
        structure_dict = structure_dict['_root']

    #print(ctx['path'], structure_dict)

    if not isinstance(structure_dict, dict):
        #return _reduce(structure_dict)
        return structure_dict

    for _key, _value in list(structure_dict.items()):
        print('check:  {}{} (ctx: {})'.format('  '*len(ctx['path']), _key, ctx))
        if ctx['in_namespace'] is not None:
            # inside a controlled namespace: value must be a dict (keys can be arbitrary)
            assert isinstance(_value, dict), "Expecting value of type 'dict' in namespace '{}'; got {}, which is of type {}.".format(ctx['in_namespace'], _value, type(_value))            
            # propagate down through namespace
            for _dir, _dir_struct in _value.items():
                #_dir_struct = _evaluate_structure(_dir_struct, ctx=dict(ctx, path=ctx['path']+[_dir], in_namespace=(None if ctx['in_namespace'] == '_dirs' else ctx['in_namespace']))
                _dir_struct = _evaluate_structure(_dir_struct, ctx=dict(ctx, path=ctx['path']+[_dir], in_namespace='_features' if ctx['in_namespace'] == '_features' else None))

        else:
            # NOT inside a controlled namespace: only reserved keys allowed
            if _key not in RESERVED_KEYWORDS:
                # reached a leaf -> compare
                structure_dict[_key] = _reduce(_value)

            #elif _key == '_objects':
            #    assert len(_value) == ctx['n_files'], "Mismatch between entry size ({}) and number of files ({})".format(len(_value), ctx['n_files'])
            #    _all = reduce(set.intersection, _value)
            #    _diff = [_val.difference(_all) for _val in _value]
            #    structure_dict['_diff'] = _diff

            elif _key == '_diff':
                pass  # ingore diffs from any previous run

            elif _key in ('_dirs', '_objects', '_features'):
                # propagate down through namespace
                for _dir, _dir_struct in _value.items():
                    _dir_struct = _evaluate_structure(_dir_struct, ctx=dict(ctx, path=ctx['path']+[_dir], in_namespace=_key))

            else:
                # something went wrong
                assert False, "Internal error: unknown keyword '{}' encountered, but it is not in RESERVED_KEYWORDS!".format(_key)

    return structure_dict

if __name__ == '__main__':
    #ap = ArgumentParser()
    
    _files = sys.argv[1:]
    #assert len(_files) == 2

    #_file_labels = list(range(len(_files)))

    _struct = {}
    _all_list_dicts_check_length = []
    for _file in _files:
        with root_open(_file, 'r') as _f:
            _struct, _list_dicts_check_length = _extract_structure(_f, _struct)
            #_all_list_dicts_check_length += _list_dicts_check_length

    #_complete_list(len(_files), _all_list_dicts_check_length)
    _complete_list(len(_files), _list_dicts_check_length)
    yaml.dump(_struct, sys.stdout, default_flow_style=None, width=40000)
    #_struct = _evaluate_structure(_struct)
    #yaml.dump(_struct, sys.stdout, default_flow_style=None)

