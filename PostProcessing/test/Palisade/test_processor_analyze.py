import numpy as np
import operator as op
import os
import shutil
import unittest2 as unittest

from copy import deepcopy

from rootpy import asrootpy
from rootpy.io import root_open, DoesNotExist
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency, Graph
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase

from DijetAnalysis.PostProcessing.Palisade import AnalyzeProcessor, InputROOT


class TestAnalyzeProcessor(unittest.TestCase):
    INPUT_FILENAME = 'ref/test.root'
    OUTPUT_FOLDER = '_test_processor_analyze'
    OUTPUT_FILENAME = 'out.root'
    #MANDATORY_CONFIG_KEYS = ['input_files', 'expansions', 'tasks']
    MANDATORY_CONFIG_KEYS = ['input_files']  # TODO: update after implementing strict checking

    BASE_CFG = {
        'input_files': {
            'test': INPUT_FILENAME
        },
        'tasks': [
            {
                'filename': OUTPUT_FILENAME,
                'subtasks': []
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
            'h2': cls._IC.get(object_spec="ref:h2")
        }

        # add "virtual" file that will contain the test outputs to compare
        cls._TEST_FILENAME = os.path.join(cls.OUTPUT_FOLDER, cls.OUTPUT_FILENAME)
        cls._IC.add_file(cls._TEST_FILENAME, nickname='test')

    @classmethod
    def tearDownClass(cls):
        # delete files created by test
        if os.path.exists(cls.OUTPUT_FOLDER):
            shutil.rmtree(cls.OUTPUT_FOLDER)

    @staticmethod
    def _run_palisade(config):
        _p = AnalyzeProcessor(
            config,
            output_folder=TestAnalyzeProcessor.OUTPUT_FOLDER
        )
        _p.run(show_progress=False)

    def _assert_rootpy_hist_equal(self, hist_1, hist_2):
        # bin-by-bin comparison
        for _bin_1, _bin_2 in zip(hist_1, hist_2):
            self.assertEqual(_bin_1.value, _bin_2.value)
            self.assertEqual(_bin_1.error, _bin_2.error)

    def test_missing_config_keys_raise(self):
        for _key in self.MANDATORY_CONFIG_KEYS:
            _cfg = deepcopy(self.BASE_CFG)
            del _cfg[_key]
            with self.subTest(key=_key):
                with self.assertRaises(KeyError) as _err:
                    self._run_palisade(config=_cfg)

                self.assertEqual(_err.exception.args[0], _key)

    def test_copy_objects(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:h1"',
            'output_path': "h1"
        })
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:h2"',
            'output_path': "h2"
        })

        self._run_palisade(config=_cfg)

        for _obj_name in ['h1', 'h2']:
            with self.subTest(object_name=_obj_name):
                _obj_ref = self._REF_OBJECTS[_obj_name]
                _obj_test = self._IC.get_expr('"test:{}"'.format(_obj_name))

                self._assert_rootpy_hist_equal(_obj_ref, _obj_test)

    def test_copy_objects_with_expansions(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:{obj[name]}"',
            'output_path': "{obj[name]}"
        })

        _cfg['expansions'].update({
            'obj': [
                {'name': 'h1'},
                {'name': 'h2'}
            ]
        })

        self._run_palisade(config=_cfg)

        for _obj_name in ['h1', 'h2']:
            with self.subTest(object_name=_obj_name):
                _obj_ref = self._REF_OBJECTS[_obj_name]
                _obj_test = self._IC.get_expr('"test:{}"'.format(_obj_name))

                self._assert_rootpy_hist_equal(_obj_ref, _obj_test)

    def test_arithmetic(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:h1" + "test:h2"',
            'output_path': "sum"
        })
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:h1" * "test:h2"',
            'output_path': "product"
        })

        self._run_palisade(config=_cfg)

        for _result_name, _op in [('sum', op.add), ('product', op.mul)]:
            with self.subTest(result_name=_result_name):
                _obj_ref = _op(self._REF_OBJECTS['h1'], self._REF_OBJECTS['h2'])
                _obj_test = self._IC.get_expr('"test:{}"'.format(_result_name))

                self._assert_rootpy_hist_equal(_obj_ref, _obj_test)

    def test_arithmetic_with_expansions(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['tasks'][0]['subtasks'].append({
            'expression': '"test:h1" {operation[operator]} "test:h2"',
            'output_path': "operation[name]"
        })
        _cfg['expansions'].update({
            'operation': [
                {'name': 'sum',     'operator': '+'},
                {'name': 'product', 'operator': '*'},
            ]
        })

        self._run_palisade(config=_cfg)

        #for _result_name, _op in [('sum', op.add), ('product', op.mul)]:
        #    with self.subTest(result_name=_result_name):
        #        _obj_ref = _op(self._REF_OBJECTS['h1'], self._REF_OBJECTS['h2'])
        #        _obj_test = self._IC.get_expr('"test:{}"'.format(_result_name))

        #        self._assert_rootpy_hist_equal(_obj_ref, _obj_test)

