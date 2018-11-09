import math
import os
import ROOT

from copy import deepcopy

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from matplotlib.ticker import LogFormatter
from matplotlib.colors import LogNorm, Normalize


from rootpy import asrootpy
from rootpy.context import preserve_current_directory
from rootpy.io import root_open, DoesNotExist, File
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase


from .._input import InputROOT
from .._colormaps import viridis

from ._base import ContextValue, LiteralString, _ProcessorBase, _make_directory

__all__ = ['AnalyzeProcessor']



class AnalyzeProcessor(_ProcessorBase):
    """Processor for analyzing objects from ROOT files. A ROOT file is written"""

    CONFIG_KEY_FOR_TEMPLATES = "tasks"
    SUBKEYS_FOR_CONTEXT_REPLACING = ["subtasks"]
    CONFIG_KEY_FOR_CONTEXTS = "expansions"


    def __init__(self, config, output_folder):
        super(AnalyzeProcessor, self).__init__(config, output_folder)

        self._input_controller = InputROOT(
            files_spec=self._config['input_files']
        )
        self._global_request_params = self._config.get("global_request_params", {})
        self._files = {}

    def _get_file(self, filename):
        if filename not in self._files:
            _fullpath = os.path.join(self._output_folder, filename)
            _make_directory(os.path.dirname(_fullpath))
            self._files[filename] = File.Open(_fullpath, 'w')
        return self._files[filename]


    # -- actions

    def _request(self, config):
        '''request all objects encountered in all subplot expressions'''
        for _subplot_cfg in config['subtasks']:
            request_params = dict(self._global_request_params, **_subplot_cfg.get('request_params', {}))
            self._input_controller._request_all_objects_in_expression(_subplot_cfg['expression'], **request_params)
            print 'REQ', _subplot_cfg['expression']

    def _process(self, config):
        '''process all tasks'''

        _tfile = self._get_file(config['filename'])

        with preserve_current_directory():
            for _subtask_config in config['subtasks']:
                _expression = _subtask_config['expression']
                _output_path = _subtask_config['output_path']

                _basename = os.path.basename(_output_path)
                _dirname = os.path.dirname(_output_path)

                ROOT.gROOT.cd()
                _plot_object = asrootpy(self._input_controller.get_expr(_expression).Clone(_basename))

                try:
                    _dir = _tfile.GetDirectory(_dirname)
                except DoesNotExist:
                    _dir = _tfile.mkdir(_dirname, recurse=True)

                _dir.cd()
                _plot_object.SetDirectory(_dir)
                _plot_object.Write()

                print "{} -> {}".format(_expression, _output_path)

    def _close_files(self, config):
        '''close all files opened by expanded configs'''
        if config['filename'] in self._files:
            _tfile = self._get_file(config['filename'])
            _tfile.Close()
            del self._files[config['filename']]


    # -- register action slots

    _ACTIONS = [_request, _process, _close_files]

