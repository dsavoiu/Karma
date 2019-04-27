import math
import numpy as np
import operator as op
import os
import shutil
import unittest2 as unittest
import yaml

from copy import deepcopy

from rootpy import asrootpy
from rootpy.io import root_open, DoesNotExist
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency, Graph
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase

from Karma.PostProcessing.Palisade import PlotProcessor, InputROOT


class TestPlotProcessor(unittest.TestCase):
    INPUT_FILENAME = 'ref/test.root'
    OUTPUT_FOLDER = '_test_processor_plot'
    OUTPUT_FILENAME = 'plot.png'
    #MANDATORY_CONFIG_KEYS = ['input_files', 'expansions', 'tasks']
    MANDATORY_CONFIG_KEYS = ['input_files']  # TODO: update after implementing strict checking

    BASE_CFG = {
        'input_files': {
            'test': INPUT_FILENAME
        },
        'figures': [
            {
                'filename': OUTPUT_FILENAME,
                'dump_yaml': True,
                'subplots': []
            }
        ],
        'expansions': {}
    }

    @classmethod
    def setUpClass(cls):
        # create root file controller
        cls._IC = InputROOT()

        # add file containing reference objects and retrieve them
        cls._IC.add_file(cls.INPUT_FILENAME, nickname='ref')
        cls._REF_OBJECTS = {
            'h1': cls._IC.get(object_spec="ref:h1"),
            'h2': cls._IC.get(object_spec="ref:h2"),
            'fa1': cls._IC.get(object_spec="ref:fa1")
        }

        # path to file(s) that will contain the test outputs to compare
        cls._TEST_FILENAME_FIG = os.path.join(cls.OUTPUT_FOLDER, cls.OUTPUT_FILENAME)
        cls._TEST_FILENAME_YML = '.'.join(cls._TEST_FILENAME_FIG.split('.')[:-1] + ['yml'])

    @classmethod
    def tearDownClass(cls):
        # delete files created by test
        if os.path.exists(cls.OUTPUT_FOLDER):
            shutil.rmtree(cls.OUTPUT_FOLDER)

    @staticmethod
    def _run_palisade(config):
        _p = PlotProcessor(
            config,
            output_folder=TestPlotProcessor.OUTPUT_FOLDER
        )
        _p.run(show_progress=False)

    def _assert_yml_equal_to_ref(self, yml_dict, root_hist):
        self.assertEqual(list(root_hist.x()), yml_dict['plot_args']['args'][0])
        self.assertEqual(list(root_hist.y()), yml_dict['plot_args']['args'][1])
        self.assertEqual(list(root_hist.xerrl()), yml_dict['plot_args']['xerr'][0])
        self.assertEqual(list(root_hist.xerrh()), yml_dict['plot_args']['xerr'][1])
        self.assertEqual(list(root_hist.yerrl()), yml_dict['plot_args']['yerr'][0])
        self.assertEqual(list(root_hist.yerrh()), yml_dict['plot_args']['yerr'][1])


    def test_missing_config_keys_raise(self):
        for _key in self.MANDATORY_CONFIG_KEYS:
            _cfg = deepcopy(self.BASE_CFG)
            del _cfg[_key]
            with self.subTest(key=_key):
                with self.assertRaises(KeyError) as _err:
                    self._run_palisade(config=_cfg)

                self.assertEqual(_err.exception.args[0], _key)

    def test_plot_histograms(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
        })
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h2"',
        })

        self._run_palisade(config=_cfg)


        with open(self._TEST_FILENAME_YML) as _f:
            _yml = yaml.load(_f)

        for _obj_name in ['h1', 'h2']:
            _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:{}"'.format(_obj_name)]
            assert len(_obj_yml_dicts) == 1  # should be unique
            self._assert_yml_equal_to_ref(_obj_yml_dicts[0], self._REF_OBJECTS[_obj_name])

    def test_plot_functions(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:fa1"',
        })

        self._run_palisade(config=_cfg)


        with open(self._TEST_FILENAME_YML) as _f:
            _yml = yaml.load(_f)

        for _obj_name in ['fa1']:
            _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:{}"'.format(_obj_name)]
            assert len(_obj_yml_dicts) == 1  # should be unique
            _yml_dict = _obj_yml_dicts[0]
            _root_tf1 = self._REF_OBJECTS[_obj_name]
            # the TF1 evaluated at each 'x' should give 'y'
            for _ref, _test in zip(list(map(_root_tf1, _yml_dict['plot_args']['args'][0])), _yml_dict['plot_args']['args'][1]):
                # handle 'nan' equality
                if math.isnan(_ref):
                    self.assertTrue(math.isnan(_test))
                else:
                    self.assertEqual(_ref, _test)

    @unittest.skip("use case not supported yet")
    def test_plot_objects_with_expansions_same_output(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:{obj[name]}"',
        })

        _cfg['expansions'].update({
            'obj': [
                {'name': 'h1'},
                {'name': 'h2'}
            ]
        })

        self._run_palisade(config=_cfg)

        with open(self._TEST_FILENAME_YML) as _f:
            _yml = yaml.load(_f)

        for _obj_name in ['h1', 'h2']:
            _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:{}"'.format(_obj_name)]
            self.assertEqual(len(_obj_yml_dicts), 1)  # subplot should be present and unique
            self._assert_yml_equal_to_ref(_obj_yml_dicts[0], self._REF_OBJECTS[_obj_name])

    def test_plot_objects_with_expansions_different_outputs(self):
        _cfg = deepcopy(self.BASE_CFG)
        _output_basename_pattern = "plot_{obj[name]}"
        _cfg['figures'][0]['filename'] = "{}.png".format(_output_basename_pattern)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:{obj[name]}"',
        })

        _cfg['expansions'].update({
            'obj': [
                {'name': 'h1'},
                {'name': 'h2'}
            ]
        })

        self._run_palisade(config=_cfg)

        _yaml_file_pattern = os.path.join(self.OUTPUT_FOLDER, "{}.yml".format(_output_basename_pattern))
        for _obj_name in ['h1', 'h2']:
            with open(_yaml_file_pattern.format(obj=dict(name=_obj_name))) as _f:
                _yml = yaml.load(_f)

            _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:{}"'.format(_obj_name)]
            self.assertEqual(len(_obj_yml_dicts), 1)  # subplot should be present and unique
            self._assert_yml_equal_to_ref(_obj_yml_dicts[0], self._REF_OBJECTS[_obj_name])
