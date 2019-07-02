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

try:
    # Python >= 3.3: 'mock' is in 'unittest' module
    from unittest.mock import patch, call, MagicMock, ANY
except ImportError:
    # Python < 3.3: 'mock' is external module
    from mock import patch, call, MagicMock, ANY

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

    def test_plot_efficiency(self):
        _efficiency_expr = 'efficiency("test:h1", "test:h1"+"test:h2")'
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': _efficiency_expr,
        })

        self._run_palisade(config=_cfg)

        with open(self._TEST_FILENAME_YML) as _f:
            _yml = yaml.load(_f)

        _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == _efficiency_expr]
        assert len(_obj_yml_dicts) == 1  # should be unique
        _yml_dict = _obj_yml_dicts[0]
        _ref_obj = self._REF_OBJECTS['h1'] / (self._REF_OBJECTS['h1'] + self._REF_OBJECTS['h2'])

        for _ref, _x, _y in zip(_ref_obj[1:-1], _yml_dict['plot_args']['args'][0], _yml_dict['plot_args']['args'][1]):
            self.assertEqual(_ref.value, _y)
            self.assertEqual(_ref.x.center, _x)
            # TODO: test efficiency errors

    def test_plot_efficiency_graph(self):
            _efficiency_expr = 'efficiency_graph("test:h1", "test:h1"+"test:h2")'
            _cfg = deepcopy(self.BASE_CFG)
            _cfg['figures'][0]['subplots'].append({
                'expression': _efficiency_expr,
            })

            self._run_palisade(config=_cfg)

            with open(self._TEST_FILENAME_YML) as _f:
                _yml = yaml.load(_f)

            _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == _efficiency_expr]
            assert len(_obj_yml_dicts) == 1  # should be unique
            _yml_dict = _obj_yml_dicts[0]
            _ref_obj = self._REF_OBJECTS['h1'] / (self._REF_OBJECTS['h1'] + self._REF_OBJECTS['h2'])

            # only nonzero bins are shown with `efficiency_graph`
            _ref_nonzero = [_ref for _ref in _ref_obj if _ref.value]

            for _ref, _x, _y in zip(_ref_nonzero, _yml_dict['plot_args']['args'][0], _yml_dict['plot_args']['args'][1]):
                self.assertEqual(_ref.value,  _y)
                self.assertEqual(_ref.x.center, _x)

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


    # -- test matplotlib calls

    def test_plot_method_default(self):
        _ref_x = list(self._REF_OBJECTS['h1'].x())
        _ref_y = list(self._REF_OBJECTS['h1'].y())

        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
        })

        with patch('matplotlib.axes.Axes.errorbar') as mock_plot:
            self._run_palisade(config=_cfg)

        self.assertEqual(len(mock_plot.mock_calls), 1)
        for _call in mock_plot.mock_calls:
            _, _args, _kwargs = _call
            self.assertEqual(len(_args), 2)  # both 'x' and 'y' supplied
            np.testing.assert_array_equal(_args[0], _ref_x)
            np.testing.assert_array_equal(_args[1], _ref_y)

    def test_plot_method_explicit(self):
        _ref_x = list(self._REF_OBJECTS['h1'].x())
        _ref_y = list(self._REF_OBJECTS['h1'].y())

        for _plot_method in ('errorbar', 'bar'):
            with self.subTest(plot_method=_plot_method):
                _cfg = deepcopy(self.BASE_CFG)
                _cfg['figures'][0]['subplots'].append({
                    'expression': '"test:h1"',
                    'plot_method': _plot_method,
                    'color': 'bogus_color'
                })

                with patch('matplotlib.axes.Axes.{}'.format(_plot_method)) as mock_plot:
                    self._run_palisade(config=_cfg)

                self.assertEqual(len(mock_plot.mock_calls), 1)
                for _call in mock_plot.mock_calls:
                    _, _args, _kwargs = _call
                    self.assertEqual(len(_args), 2)  # both 'x' and 'y' supplied
                    np.testing.assert_array_equal(_args[0], _ref_x)
                    np.testing.assert_array_equal(_args[1], _ref_y)
                    if _plot_method == 'bar':
                        self.assertIn('ecolor', _kwargs)
                        self.assertEqual(_kwargs['ecolor'], _cfg['figures'][0]['subplots'][-1]['color'])

    def test_plot_method_external_override(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
            'plot_method': 'bogus_plot_method',
        })

        # just in case
        assert "bogus_plot_method" not in PlotProcessor._EXTERNAL_PLOT_METHODS

        # different patching strategy
        with MagicMock() as mock_plot:
            PlotProcessor._EXTERNAL_PLOT_METHODS["bogus_plot_method"] = mock_plot

            self._run_palisade(config=_cfg)

            del PlotProcessor._EXTERNAL_PLOT_METHODS["bogus_plot_method"]

        mock_plot.assert_called()

    def test_plot_method_step_default(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
            'plot_method': 'step',
        })

        with patch('matplotlib.axes.Axes.errorbar') as mock_errorbar:
            self._run_palisade(config=_cfg)

        mock_errorbar.assert_called_once_with(ANY, ANY, yerr=None, capsize=ANY)

    def test_plot_method_step_show_yerr_as(self):

        _ref_x = list(self._REF_OBJECTS['h1'].x())
        _ref_y = list(self._REF_OBJECTS['h1'].y())

        for _show_yerr_as in ('errorbar', 'band', None):
            with self.subTest(show_yerr_as=_show_yerr_as):

                _cfg = deepcopy(self.BASE_CFG)
                _cfg['figures'][0]['subplots'].append({
                    'expression': '"test:h1"',
                    'plot_method': 'step',
                    'show_yerr_as': _show_yerr_as,
                })

                _ref_yerr = None  # for both None and 'band'
                if _show_yerr_as == 'errorbar':
                    _ref_yerr = np.asarray(list(self._REF_OBJECTS['h1'].yerr())).T

                with patch('matplotlib.axes.Axes.errorbar') as mock_errorbar:
                    with patch('matplotlib.axes.Axes.fill_between') as mock_fill_between:
                        self._run_palisade(config=_cfg)

                self.assertEqual(len(mock_errorbar.mock_calls), 1)
                for _call in mock_errorbar.mock_calls:
                    _, _args, _kwargs = _call
                    self.assertEqual(len(_args), 2)  # both 'x' and 'y' supplied
                    np.testing.assert_array_equal(_args[0][1:-1:3], _ref_x)
                    np.testing.assert_array_equal(_args[1][1:-1:3], _ref_y)
                    self.assertIn('yerr', _kwargs)   # 'yerr' supplied
                    if _ref_yerr is None:
                        self.assertIs(_kwargs['yerr'], None)
                    else:
                        np.testing.assert_array_equal(_kwargs['yerr'][0][1:-1:3], _ref_yerr[0])
                        np.testing.assert_array_equal(_kwargs['yerr'][1][1:-1:3], _ref_yerr[1])

                if _show_yerr_as == 'band':
                    # recover 'yerr' (was None for testing 'errorbar' call)
                    _ref_yerr = np.asarray(list(self._REF_OBJECTS['h1'].yerr())).T
                    self.assertEqual(len(mock_fill_between.mock_calls), 1)
                    for _call in mock_fill_between.mock_calls:
                        _, _args, _kwargs = _call
                        self.assertEqual(len(_args), 3)  # 'x', 'y_lo' and 'y_hi' all supplied
                        np.testing.assert_array_equal(_args[0][1:-1:3], _ref_x)
                        np.testing.assert_array_equal(_args[1][1:-1:3], _ref_y-_ref_yerr[0])
                        np.testing.assert_array_equal(_args[2][1:-1:3], _ref_y+_ref_yerr[1])

    def test_plot_method_pcolormesh_default(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['input_files']['test'] = 'ref/test_2.root'  # 2d object in different file
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h2d"',
            'plot_method': 'pcolormesh',
        })

        with patch('matplotlib.axes.Axes.pcolormesh') as mock_plot:
            with patch('matplotlib.figure.Figure.colorbar') as mock_colorbar:
                self._run_palisade(config=_cfg)

        mock_plot.assert_called()
        for _call in mock_plot.mock_calls:
            _, _args, _kwargs = _call
            self.assertEqual(len(_args), 3)  # 'x', 'y' and 'z' all supplied

    def test_plot_method_pcolormesh_cmap(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['input_files']['test'] = 'ref/test_2.root'  # 2d object in different file
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h2d"',
            'plot_method': 'pcolormesh',
            'cmap': 'viridis'
        })

        with patch('matplotlib.axes.Axes.pcolormesh') as mock_plot:
            with patch('matplotlib.figure.Figure.colorbar') as mock_colorbar:
                self._run_palisade(config=_cfg)

        mock_plot.assert_called()
        for _call in mock_plot.mock_calls:
            _, _args, _kwargs = _call
            self.assertEqual(len(_args), 3)  # 'x', 'y' and 'z' all supplied
            self.assertIn('cmap', _kwargs)
            self.assertEqual(_kwargs['cmap'], 'viridis')

    # -- test pad functionality

    def test_pad_missing_raise(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
            'pad': 1  # not defined
        })

        with self.assertRaises(ValueError):
            self._run_palisade(config=_cfg)


    def test_pad_lines_simple_values(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['filename'] = "test_pad_lines.png"
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
        })
        _cfg['figures'][0]['pads'] = [{
            'axhlines': [0.0, 1.0],
            'axvlines': [2.0, 3.0],
        }]

        with patch('matplotlib.axes.Axes.axhline') as mock_axhline:
            with patch('matplotlib.axes.Axes.axvline') as mock_axvline:
                self._run_palisade(config=_cfg)

        _calls_axhline = [call(_val, **PlotProcessor._DEFAULT_LINE_KWARGS) for _val in _cfg['figures'][0]['pads'][0]['axhlines']]
        _calls_axvline = [call(_val, **PlotProcessor._DEFAULT_LINE_KWARGS) for _val in _cfg['figures'][0]['pads'][0]['axvlines']]
        mock_axhline.assert_has_calls(_calls_axhline, any_order=True)
        mock_axvline.assert_has_calls(_calls_axvline, any_order=True)

    def test_pad_lines_dictionaries(self):
        _axhline_dict = dict(color='r', linestyle='--')
        _axvline_dict = dict(color='b', zorder=1234)

        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['filename'] = "test_pad_lines.png"
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
        })
        _cfg['figures'][0]['pads'] = [{
            'axhlines': [dict(_axhline_dict, values=[0.0, 1.0])],
            'axvlines': [dict(_axvline_dict, values=[2.0, 3.0])],
        }]

        with patch('matplotlib.axes.Axes.axhline') as mock_axhline:
            with patch('matplotlib.axes.Axes.axvline') as mock_axvline:
                self._run_palisade(config=_cfg)

        _calls_axhline = [call(_val, **dict(PlotProcessor._DEFAULT_LINE_KWARGS, **_axhline_dict)) for _val in _cfg['figures'][0]['pads'][0]['axhlines'][0]['values']]
        _calls_axvline = [call(_val, **dict(PlotProcessor._DEFAULT_LINE_KWARGS, **_axvline_dict)) for _val in _cfg['figures'][0]['pads'][0]['axvlines'][0]['values']]
        mock_axhline.assert_has_calls(_calls_axhline, any_order=True)
        mock_axvline.assert_has_calls(_calls_axvline, any_order=True)

    def test_plot_expression_referencing(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': '"test:h1"',
        })
        _cfg['figures'][0]['subplots'].append({
            'expression': 'expressions[0]',
        })

        self._run_palisade(config=_cfg)

        with open(self._TEST_FILENAME_YML) as _f:
            _yml = yaml.load(_f)

        _obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:h1"' or _d['expression'] == 'expressions[0]']
        assert len(_obj_yml_dicts) == 2  # should be present twice
        self._assert_yml_equal_to_ref(_obj_yml_dicts[0], self._REF_OBJECTS['h1'])
        self._assert_yml_equal_to_ref(_obj_yml_dicts[1], self._REF_OBJECTS['h1'])

    def test_plot_expression_circular_reference_raise(self):
        _cfg = deepcopy(self.BASE_CFG)
        _cfg['figures'][0]['subplots'].append({
            'expression': 'expressions[0]',
        })

        with self.assertRaises(NameError) as _err:
            self._run_palisade(config=_cfg)

        #with open(self._TEST_FILENAME_YML) as _f:
        #    _yml = yaml.load(_f)

        #_obj_yml_dicts = [_d for _d in _yml['subplots'] if _d['expression'] == '"test:h1"' or _d['expression'] == 'expressions[0]']
        #assert len(_obj_yml_dicts) == 1  # should be present twice
        #self._assert_yml_equal_to_ref(_obj_yml_dicts[0], self._REF_OBJECTS['h1'])
        #self._assert_yml_equal_to_ref(_obj_yml_dicts[1], self._REF_OBJECTS['h1'])
