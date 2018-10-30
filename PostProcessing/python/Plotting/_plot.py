import abc
import argparse
import ast
import itertools
import math
import os
import sys

from array import array
from copy import deepcopy

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.font_manager import FontProperties
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import LogFormatter
from matplotlib.colors import LogNorm, Normalize

from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase

from ._input import InputROOT
from ._colormaps import viridis

__all__ = ['DijetLogFormatterSciNotation', 'Plotter', 'ContextValue', 'LiteralString']


plt.register_cmap(name='viridis', cmap=viridis)

def _mplrc():
    mpl.rc('mathtext', fontset='stixsans', fallback_to_cm=False, rm='sans')
    mpl.rc('axes', labelsize=16)
    mpl.rc('legend', labelspacing=.1, fontsize=8)

def _mathdefault(s):
    return '\\mathdefault{%s}' % s

def is_close_to_int(x):
    if not np.isfinite(x):
        return False
    return abs(x - round(x)) < 1e-10

def _make_directory(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno == 17:  # File exists
            pass
        else:
            raise

class DijetLogFormatterSciNotation(LogFormatter):

    def __call__(self, x, pos=None):
        """
        Return the format for tick value *x*.

        The position *pos* is ignored.
        """
        usetex = mpl.rcParams['text.usetex']
        min_exp = 0 #mpl.rcParams['axes.formatter.min_exponent']

        if x == 0:  # Symlog
            if usetex:
                return '$0$'
            else:
                return '$%s$' % _mathdefault('0')

        sign_string = '-' if x < 0 else ''
        x = abs(x)
        b = self._base

        # only label the decades
        fx = math.log(x) / math.log(b)
        is_x_decade = is_close_to_int(fx)
        exponent = np.round(fx) if is_x_decade else np.floor(fx)
        coeff = np.round(x / b ** exponent)
        if is_x_decade:
            fx = round(fx)

        if self.labelOnlyBase and not is_x_decade:
            return ''
        if self._sublabels is not None and coeff not in self._sublabels:
            return ''

        # use string formatting of the base if it is not an integer
        if b % 1 == 0.0:
            base = '%d' % b
        else:
            base = '%s' % b

        if np.abs(fx) < min_exp:
            if usetex:
                return r'${0}{1:g}$'.format(sign_string, x)
            else:
                return '${0}$'.format(_mathdefault(
                    '{0}{1:g}'.format(sign_string, x)))
        elif not is_x_decade:
            return self._non_decade_format(sign_string, base, fx, usetex)
        elif usetex:
            return r'$%s%s^{%d}$' % (sign_string, base, fx)
        else:
            return '$%s$' % _mathdefault('%s%s^{%d}' % (sign_string, base, fx))

    def _non_decade_format(self, sign_string, base, fx, usetex):
        'Return string for non-decade locations'
        b = float(base)
        exponent = math.floor(fx)
        coeff = b ** fx / b ** exponent
        if is_close_to_int(coeff):
            coeff = round(coeff)
        if usetex:
            return (r'$%s%g\times%s^{%d}$') % \
                                        (sign_string, coeff, base, exponent)
        else:
            return ('$%s$' % _mathdefault(r'%s%g\times%s^{%d}' %
                                        (sign_string, coeff, base, exponent)))

    def set_locs(self, *args, **kwargs):
        '''override sublabels'''
        _ret = super(DijetLogFormatterSciNotation, self).set_locs(*args, **kwargs)

        # override locations
        _locs = kwargs.pop("locs", None)
        if _locs is not None:
            self._sublabels = _locs
        else:
            self._sublabels = {1.0, 2.0, 5.0, 10.0}

        return _ret


def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))


class ConfigurationError(Exception):
    pass


class ConfigurationEntry(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, context):
        raise NotImplementedError


class ContextValue(ConfigurationEntry):
    """Configuration object. Is replaced by the value corresponding to the `key` in the current context."""
    __slots__ = ['path']
    def __init__(self, path):
        self.path = path

    @staticmethod
    def _eval(node, context):
        """Evaluate an AST node"""
        if isinstance(node, ast.Str): # <string> : simple lookup
            return context[node.s]

        elif isinstance(node, ast.Name): # <identifies> : same treatment as string
            return context[node.id]

        elif isinstance(node, ast.Subscript):  # <left>[<right>]
            # expr = 'asmz_fit_value[ERRORS_LABEL=="exp+np+pdf"]'
            # node.value = {_ast.Name}
            # node.value.id = '<left>'
            # node.slice.value = {_ast.Str}
            # node.slice.value.s = {str} '<right>'

            _lnode = node.value
            _rnode = node.slice.value

            _inner_ctx = ContextValue._eval(_lnode, context)
            return ContextValue._eval(_rnode, _inner_ctx)

        else:
            raise ConfigurationError("Cannot interpret context node: {}".format(node))

    def get(self, context):
        return self._eval(ast.parse(self.path, mode='eval').body, context)


class LiteralString(ConfigurationEntry):
    """Configuration object. Used for strings containing curly braces to avoid test substitution."""
    __slots__ = ['s']
    def __init__(self, string):
        self.s = string

    def get(self, context):
        return self.s


class Plotter(object):

    FONT_PROPS = dict(
        big_bold=FontProperties(
            weight='bold',
            family='Nimbus Sans',
            size=20,
        ),
        small_bold=FontProperties(
            weight='bold',
            family='Nimbus Sans',
            size=12,
        ),
        italic=FontProperties(
            style='italic',
            family='Nimbus Sans',
            size=14,
        ),
    )

    _PC_KEYS_MPL_AXES_METHODS = dict(
        x_label = dict(
            method='set_xlabel',
            kwargs=dict(x=1.0, ha='right'),
        ),
        y_label = dict(
            method='set_ylabel',
            kwargs=dict(y=1.0, ha='right'),
        ),
        x_range = dict(
            method='set_xlim',
        ),
        y_range = dict(
            method='set_ylim',
        ),
        x_scale = dict(
            method='set_xscale',
        ),
        y_scale = dict(
            method='set_yscale',
        ),
        x_ticklabels = dict(
            method='set_xticklabels',
        ),
        y_ticklabels = dict(
            method='set_yticklabels',
        ),
    )

    _DEFAULT_LEGEND_KWARGS = dict(
        ncol=1, numpoints=1, fontsize=12, frameon=False,
        loc='upper right'
    )

    def __init__(self, config, output_folder):
        self._config = config
        self._output_folder = output_folder
        self._input_controller = InputROOT(
            files_spec=self._config['input_files']
        )
        self._figures = {}
        self._global_request_params = self._config.get("global_request_params", {})

    def _get_figure(self, figure_name, figsize=None):
        if figure_name not in self._figures:
            self._figures[figure_name] = plt.figure(figsize=figsize)
        return self._figures[figure_name]

    def _run_with_context(self, context):
        # TODO: make more general
        for _fig_cfg in self._config['figures']:
            _fig_cfg = deepcopy(_fig_cfg)
            for _k, _v in _fig_cfg.iteritems():
                if isinstance(_v, str):
                    _fig_cfg[_k] = _v.format(**context)
                elif isinstance(_v, ConfigurationEntry):
                    _fig_cfg[_k] = _v.get(context)

            for _subkey_for_context_replacing in ('pads', 'subplots'):
                for _dict_for_subkey in _fig_cfg[_subkey_for_context_replacing]:
                    for _k, _v in _dict_for_subkey.iteritems():
                        if isinstance(_v, str):
                            _dict_for_subkey[_k] = _v.format(**context)
                        elif isinstance(_v, ConfigurationEntry):
                            _dict_for_subkey[_k] = _v.get(context)

            self._plot_figure(_fig_cfg)

    def _request_all_expressions_with_context(self, context, **request_params):
        _reqs = []
        for _fig_cfg in self._config['figures']:
            # override global request parameters, if requested
            request_params.update(_fig_cfg.get('request_params', {}))
            for _subplot_dict in _fig_cfg['subplots']:
                 #_reqs.append(dict(object_spec=_subplot_dict['expression'].format(**context)))
                self._input_controller._request_all_objects_in_expression(_subplot_dict['expression'].format(**context), **request_params)

        #self._input_controller.request(_reqs)

    @staticmethod
    def _merge_legend_handles_labels(handles, labels):
        '''merge handles for identical labels'''
        _seen_labels = []
        _seen_label_handles = []
        _new_label_indices = []
        for _ihl, (_h, _l) in enumerate(zip(handles, labels)):
            if _l not in _seen_labels:
                _seen_labels.append(_l)
                _seen_label_handles.append([_h])
            else:
                _idx = _seen_labels.index(_l)
                _seen_label_handles[_idx].append(_h)

        for _i, (_sh, _sl) in enumerate(zip(_seen_label_handles, _seen_labels)):
            _seen_label_handles[_i] = tuple(_seen_label_handles[_i])

        return _seen_label_handles, _seen_labels

    def _plot_figure(self, plot_config):

        _mplrc()

        _filename = os.path.join(self._output_folder, plot_config['filename'])

        _figsize = plot_config.pop('figsize', None)
        _fig = self._get_figure(_filename, figsize=_figsize)

        # obtain configuration of pads
        _pad_configs = plot_config.get('pads', None)
        if _pad_configs is None:
            # default pad configuration
            _pad_configs = [dict()]

        # get share
        _height_ratios = [_pc.get('height_share', 1) for _pc in _pad_configs]

        # construct GridSpec from `pad_spec` or make default
        _gridspec_kwargs = plot_config.get('pad_spec', dict())
        _gridspec_kwargs.pop('height_ratios', None)   # ignore explicit user-provided `height_ratios`
        _gs = GridSpec(nrows=len(_pad_configs), ncols=1, height_ratios=_height_ratios, **_gridspec_kwargs)

        # store `Axes` objects in pad configuration
        for _i_pad, _pad_config in enumerate(_pad_configs):
            _pad_config['axes'] = _fig.add_subplot(_gs[_i_pad])

        # enable text output, if requested
        if plot_config.pop("text_output", False):
            _text_filename = '.'.join(_filename.split('.')[:-1]) + '.txt'
            # need to create directory first
            _make_directory(os.path.dirname(_text_filename))
            _text_file = open(_text_filename, 'w')
        else:
            _text_file = None

        # step 2: retrieve data and plot

        for _pc in plot_config['subplots']:
            _kwargs = deepcopy(_pc)

            # obtain and validate pad ID
            _pad_id = _kwargs.pop('pad', 0)
            if _pad_id >= len(_pad_configs):
                raise ValueError("Cannot plot to pad {}: only pads up to {} have been configured!".format(_pad_id, len(_pad_configs)-1))

            # select pad axes and configuration
            _pad_config = _pad_configs[_pad_id]
            _ax = _pad_config['axes']
            _stack_bottoms = _pad_config.setdefault('stack_bottoms', {})

            _expression = _kwargs.pop('expression')
            print("PLT {}".format(_expression))
            _plot_object = self._input_controller.get_expr(_expression)

            # extract arrays for keys which could be masked by 'mask_zero_errors'
            _plot_data = {
                _property_name : np.array(list(getattr(_plot_object, _property_name)()))
                for _property_name in ('x', 'xerr', 'y', 'yerr', 'xwidth', 'efficiencies', 'errors')
                if hasattr(_plot_object, _property_name)
            }

            # map fields for TEfficiency objects
            if isinstance(_plot_object, Efficiency):
                _total_hist = _plot_object.total
                _plot_data['x'] = np.array(list(_total_hist.x()))
                _plot_data['xerr'] = np.array(list(_total_hist.xerr()))
                _plot_data['y'] = _plot_data.pop('efficiencies', None)
                _plot_data['yerr'] = _plot_data.pop('errors', None)

            # mask all points with erorrs set to zero
            _mze = _kwargs.pop('mask_zero_errors', False)
            if _mze:
                _mask = np.all((_plot_data['yerr'] != 0), axis=1)
                _plot_data = {
                    _key : np.compress(_mask, _value, axis=0)
                    for _key, _value in _plot_data.iteritems()
                }

            # extract arrays for keys which cannot be masked
            _plot_data.update({
                _property_name : np.array(list(getattr(_plot_object, _property_name)()))
                for _property_name in ('xedges', 'yedges', 'z')
                if hasattr(_plot_object, _property_name)
            })

            # -- draw

            _plot_method_name = _kwargs.pop('plot_method', 'errorbar')
            _plot_method = getattr(_ax, _plot_method_name)

            if _plot_method_name == 'errorbar':
                _kwargs.setdefault('linestyle', '')
                _kwargs.setdefault('capsize', 0)
                if 'color' in _pc:
                    _kwargs.setdefault('markeredgecolor', _kwargs['color'])

            # marker styles
            _marker_style = _kwargs.pop('marker_style', None)
            if _marker_style is not None:
                if _marker_style == 'full':
                    _kwargs.update(
                        markerfacecolor=_kwargs['color'],
                        markeredgewidth=0,
                    )
                elif _marker_style == 'empty':
                    _kwargs.update(
                        markerfacecolor='w',
                        markeredgewidth=1,
                    )
                else:
                    raise ValueError("Unkown value for 'marker_style': {}".format(_marker_style))

            # handle stacking
            _stack_name = _kwargs.pop('stack', None)
            _y_bottom = 0
            if _stack_name is not None:
                _y_bottom = _stack_bottoms.setdefault(_stack_name, 0.0)  # actually 'get' with default

            # different methods handle information differently
            if _plot_method_name == 'bar':
                _kwargs['width'] = _plot_data['xwidth']
                _kwargs.setdefault('align', 'center')
                _kwargs.setdefault('edgecolor', '')
                _kwargs.setdefault('linewidth', 0)
                if 'color' in _kwargs:
                    # make error bar color match fill color
                    _kwargs.setdefault('ecolor', _kwargs['color'])
                _kwargs['y'] = _plot_data['y']
                _kwargs['bottom'] = _y_bottom
            else:
                _kwargs['y'] = _plot_data['y'] + _y_bottom
                _kwargs['xerr'] = _plot_data['xerr'].T

            _show_yerr = _kwargs.pop('show_yerr', True)
            if _show_yerr:
                _kwargs['yerr'] = _plot_data['yerr'].T

            _y_data = _kwargs.pop('y')
            _normflag = _kwargs.pop('normalize_to_width', False)
            if _normflag:
                _y_data /= _plot_data['xwidth']
                if 'yerr' in _kwargs and _kwargs['yerr'] is not None:
                    _kwargs['yerr'] /= _plot_data['xwidth']

            # -- sort out positional arguments to plot method

            if _plot_method_name == 'pcolormesh':
                # mask zeros
                _z_masked = np.ma.array(_plot_data['z'], mask=_plot_data['z']==0)

                # determine data range in z
                _z_range = _pad_config.get('z_range', None)
                if _z_range is not None:
                    # use specified values as range
                    _z_min, _z_max = _z_range
                else:
                    # use data values
                    _z_min, _z_max = _z_masked.min(), _z_masked.max()

                # determine colormap normalization (if not explicitly given)
                if 'norm' not in _kwargs:
                    _z_scale = _pad_config.get('z_scale', "linear")
                    if _z_scale == 'linear':
                        _norm = Normalize(vmin=_z_min, vmax=_z_max)
                    elif _z_scale == 'log':
                        _norm = LogNorm(vmin=_z_min, vmax=_z_max)
                    else:
                        raise ValueError("Unknown value '{}' for keyword 'z_scale': known are {{'linear', 'log'}}".format(_z_scale))
                    _kwargs['norm'] = _norm

                # Z array needs to be transposed because 'X' refers to columns and 'Y' to rows...
                _args = [_plot_data['xedges'], _plot_data['yedges'], _z_masked.T]
                _kwargs.pop('color', None)
                _kwargs.pop('xerr', None)
                _kwargs.pop('yerr', None)
            else:
                _args = [_plot_data['x'], _y_data]

            # skip empty arguments
            if len(_args[0]) == 0:
                continue

            # run the plot method
            _plot_handle = _plot_method(
                *_args,
                **_kwargs
            )

            # store 2D plots for displaying color bars
            if _plot_method_name == 'pcolormesh':
                _pad_config.setdefault('2d_plots', []).append(_plot_handle)

            if _text_file is not None:
                np.set_printoptions(threshold=np.inf)
                _text_file.write("- {}(\n\t{},\n\t{}\n)\n".format(
                    _plot_method_name,
                    ',\n\t'.join(["{}".format(repr(_arg)) for _arg in _args]),
                    ',\n\t'.join(["{} = {}".format(_k, repr(_v)) for _k, _v in _kwargs.iteritems()]),
                ))
                np.set_printoptions(threshold=1000)

            # update stack bottoms
            if _stack_name is not None:
                _stack_bottoms[_stack_name] += _plot_data['y']

        # close text output
        if _text_file is not None:
            _text_file.close()

        # step 3: pad adjustments

        for _pad_config in _pad_configs:
            _ax = _pad_config['axes']

            # simple axes adjustments
            for _prop_name, _meth_dict in self._PC_KEYS_MPL_AXES_METHODS.iteritems():
                _prop_val = _pad_config.get(_prop_name, None)
                if _prop_val is not None:
                    #print _prop_name, _prop_val
                    getattr(_ax, _meth_dict['method'])(_prop_val, **_meth_dict.get('kwargs', {}))

            # draw colorbar if there was a 2D plot involved
            if _pad_config.get('2d_plots', None):
                for _2d_plot in _pad_config['2d_plots']:
                    _cbar = _fig.colorbar(_2d_plot, ax=_ax)
                    _z_label = _pad_config.get('z_label', None)
                    _z_labelpad = _pad_config.get('z_labelpad', None)
                    if _z_label is not None:
                        _cbar.ax.set_ylabel(_z_label, rotation=90, va="bottom", ha='right', y=1.0, labelpad=_z_labelpad)

            # draw text/annotations
            #_ax.text(.05, .9,
            #    r"CMS",
            #    ha='left',
            #    transform=ax.transAxes,
            #    fontproperties=Plotter.FONT_PROPS['big_bold']
            #)
            #_ax.text(.03, .03,
            #    r"AK4PFCHS",
            #    ha='left',
            #    transform=ax.transAxes,
            #    fontproperties=Plotter.FONT_PROPS['small_bold']
            #)
            #_ax.text(.17, .9,
            #    r"Private Work",
            #    ha='left',
            #    transform=ax.transAxes,
            #    fontproperties=Plotter.FONT_PROPS['italic']
            #)

            # handle horizontal and vertical lines
            _axhlines = _pad_config.pop('axhlines', [])
            for _y in _axhlines:
                _ax.axhline(_y, linestyle='--', color='gray')
            _axvlines = _pad_config.pop('axvlines', [])
            for _x in _axvlines:
                _ax.axvline(_x, linestyle='--', color='gray')

            # -- handle plot legend

            # obtain legend handles and labels
            _hs, _ls = _ax.get_legend_handles_labels()

            # merge legend entries with identical labels
            _hs, _ls = self._merge_legend_handles_labels(_hs, _ls)

            # draw legend with user-specified kwargs
            _legend_kwargs = self._DEFAULT_LEGEND_KWARGS.copy()
            _legend_kwargs.update(_pad_config.pop('legend_kwargs', {}))
            _ax.legend(_hs, _ls, **_legend_kwargs)

            # handle log x-axis formatting (only if 'x_ticklabels' is not given as [])
            if _pad_config.get('x_scale', None) == 'log' and _pad_config.get('x_ticklabels', True):
                _log_decade_ticklabels = _pad_config.get('x_log_decade_ticklabels', {1.0, 2.0, 5.0, 10.0})
                _formatter = DijetLogFormatterSciNotation(base=10.0, labelOnlyBase=False)
                _formatter.set_locs(locs=_log_decade_ticklabels)

                _ax.xaxis.set_minor_formatter(_formatter)

            ## handle log y-axis formatting (only if 'y_ticklabels' is not given as [])
            #if _pad_config.get('y_scale', None) == 'log' and _pad_config.get('y_ticklabels', True):
            #    _log_decade_ticklabels = _pad_config.get('y_log_decade_ticklabels', {1.0, 5.0})
            #    _formatter = DijetLogFormatterSciNotation(base=10.0, labelOnlyBase=False)
            #    _formatter.set_locs(locs=_log_decade_ticklabels)
            #
            #    _ax.yaxis.set_minor_formatter(_formatter)

        # step 4: figure adjustments

        # handle figure label ("upper_label")
        _upper_label = plot_config.pop('upper_label', None)
        if _upper_label is not None:
            # place above topmost `Axes`
            _ax_top = _pad_configs[0]['axes']
            _ax_top.text(1.0, 1.015,
                _upper_label,
                ha='right',
                transform=_ax_top.transAxes
            )

        # step 5: save figures
        _make_directory(os.path.dirname(_filename))
        _fig.savefig('{}'.format(_filename))


    # -- public API

    def clear_figures(self):
        for _fign, _fig in self._figures.iteritems():
            plt.close(_fig)
        self._figures = {}

    def run(self):

        # -- run over cross product of expansion

        # first: request all objects
        for _expansion_context in list(product_dict(**self._config['expansions'])):
            self._request_all_expressions_with_context(_expansion_context, **self._global_request_params)

        # second: actual plotting
        for _expansion_context in list(product_dict(**self._config['expansions'])):
            self._run_with_context(_expansion_context)
