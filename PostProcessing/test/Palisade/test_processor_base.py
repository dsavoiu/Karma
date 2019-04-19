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

from DijetAnalysis.PostProcessing.Palisade import ContextValue, LiteralString
from DijetAnalysis.PostProcessing.Palisade.Processors._base import _ProcessorBase, ConfigurationError
#from DijetAnalysis.PostProcessing.Palisade.Processors._base import _ProcessorBase


_RESULTS = []

class DummyProcessor(_ProcessorBase):

    CONFIG_KEY_FOR_TEMPLATES = "templates"
    SUBKEYS_FOR_CONTEXT_REPLACING = ["replace_under_here"]
    CONFIG_KEY_FOR_CONTEXTS = "expansions"

    def __init__(self, config):
        super(DummyProcessor, self).__init__(config, output_folder="dummy")
        self.results = []

    def _process(self, config):
        print(config)
        return self.results.append(config)

    # -- register action slots

    _ACTIONS = [_process]


class DummyDataStructure:
    pass


class TestProcessorBase(unittest.TestCase):
    #MANDATORY_CONFIG_KEYS = ['input_files', 'expansions', 'templates']
    MANDATORY_CONFIG_KEYS = []

    BASE_CFG = {
        'templates': [
            dict(),
        ],
        'expansions': {
            'namespace': [dict(key=42)],
        },
    }

    @staticmethod
    def _run_palisade(config):
        _p = DummyProcessor(config)
        _p.run(show_progress=False)
        return _p.results

    def test_missing_config_keys_raise(self):
        for _key in self.MANDATORY_CONFIG_KEYS:
            _cfg = deepcopy(self.BASE_CFG)
            del _cfg[_key]
            with self.subTest(key=_key):
                with self.assertRaises(KeyError) as _err:
                    self._run_palisade(config=_cfg)

                self.assertEqual(_err.exception.args[0], _key)

    def test_run_through(self):
        '''base config should run through without exceptions being raised'''
        _cfg = deepcopy(self.BASE_CFG)
        _results = self._run_palisade(config=_cfg)

    def test_number_of_contexts(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'] = [dict()] * 2  # two empty tasks...
        _cfg['expansions'] = {
            # ...times fifteen contexts
            'namespace_A': [dict(a='b')] * 3,
            'namespace_B': [dict(c='d')] * 5,
        }
        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 2*3*5)

    def test_replace_context_string(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_string': '{namespace[key]}',
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['context_string'], str(self.BASE_CFG['expansions']['namespace'][0]['key']))

    def test_replace_context_value_namespace_with_space(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['expansions'] = {
            # ...times fifteen contexts
            'namespace with space': [dict(key=42)],
        }
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_value': ContextValue('"namespace with space"[key]'),
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['context_value'], 42)

    def test_replace_context_value(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_value': ContextValue('namespace[key]'),
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['context_value'], self.BASE_CFG['expansions']['namespace'][0]['key'])

    def test_replace_context_literal_string(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'literal_string': LiteralString('{namespace[key]}'),
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['literal_string'], '{namespace[key]}')

    def test_replace_context_nested_dict(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_nested_dict': {
                  'lvl_1': { 'lvl_2': { 'inner_key': ContextValue('namespace[key]')}}
                },
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['context_nested_dict']['lvl_1']['lvl_2']['inner_key'], self.BASE_CFG['expansions']['namespace'][0]['key'])

    def test_replace_context_nested_list(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_nested_list': [[
                  { 'inner_key': ContextValue('namespace[key]')}
                ]],
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_under_here']['context_nested_list'][0][0]['inner_key'], self.BASE_CFG['expansions']['namespace'][0]['key'])

    def test_replace_context_nested_dict_list(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_nested_dict_list': {
                  'inner_key': [
                    ContextValue('namespace[key]'),
                    ContextValue('namespace[key]'),
                  ]
                },
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        for _i in range(2):
            self.assertEqual(_results[0]['replace_under_here']['context_nested_dict_list']['inner_key'][_i], self.BASE_CFG['expansions']['namespace'][0]['key'])

    def test_replace_context_nested_list_dict(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_nested_list_dict': [
                  { 'inner_key': [ContextValue('namespace[key]'), ContextValue('namespace[key]')]},
                  { 'inner_key': [ContextValue('namespace[key]'), ContextValue('namespace[key]')]}
                ],
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        for _i in range(2):
            for _j in range(2):
                self.assertEqual(_results[0]['replace_under_here']['context_nested_list_dict'][_i]['inner_key'][_j], self.BASE_CFG['expansions']['namespace'][0]['key'])


    def test_noreplace_context_not_under_key(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'dont_replace_under_here': {
                'literal_string': '{namespace[key]}',
            }
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['dont_replace_under_here']['literal_string'], '{namespace[key]}')

    def test_replace_context_string_top_level_key(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_this_as_well' : '{namespace[key]}',
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_this_as_well'], str(self.BASE_CFG['expansions']['namespace'][0]['key']))

    def test_replace_context_string_top_level_key(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_this_as_well' : ContextValue('namespace[key]'),
        })

        _results = self._run_palisade(config=_cfg)
        self.assertEqual(len(_results), 1)
        self.assertEqual(_results[0]['replace_this_as_well'], self.BASE_CFG['expansions']['namespace'][0]['key'])


    def test_context_value_unsupported_data_structure_raise(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_value': DummyDataStructure(),
            }
        })

        with self.assertRaises(ConfigurationError):
            self._run_palisade(config=_cfg)

    def test_context_value_unsupported_syntax(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['templates'][0].update({
            'replace_under_here': {
                'context_value': ContextValue('namespace+key'),
            }
        })

        with self.assertRaises(ConfigurationError):
            _results = self._run_palisade(config=_cfg)
