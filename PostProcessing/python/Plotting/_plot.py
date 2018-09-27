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
from matplotlib.ticker import LogFormatter

from ._input import InputROOT


__all__ = ['DijetLogFormatterSciNotation', 'Plotter', 'ContextValue', 'LiteralString']


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

    def _close_plot(self, ax, plot_config):
        ax.text(.05, .9,
            r"CMS",
            ha='left',
            transform=ax.transAxes,
            fontproperties=Plotter.FONT_PROPS['big_bold']
        )
        ax.text(.03, .03,
            r"AK4PFCHS",
            ha='left',
            transform=ax.transAxes,
            fontproperties=Plotter.FONT_PROPS['small_bold']
        )
        ax.text(.17, .9,
            r"Private Work",
            ha='left',
            transform=ax.transAxes,
            fontproperties=Plotter.FONT_PROPS['italic']
        )

        # handle figure label ("upper_label")
        _upper_label = plot_config.pop('upper_label', None)
        if _upper_label is not None:
            ax.text(1.0, 1.015,
                _upper_label,
                ha='right',
                transform=ax.transAxes
            )

        # handle plot legend
        _legend_kwargs = self._DEFAULT_LEGEND_KWARGS.copy()
        _legend_kwargs.update(plot_config.pop('legend_kwargs', {}))
        ax.legend(**_legend_kwargs)

        # handle log x-axis formatting
        if plot_config.get('x_scale', None) == 'log':
            _log_decade_ticklabels = plot_config.pop('log_decade_ticklabels', {1.0, 2.0, 5.0, 10.0})
            _formatter = DijetLogFormatterSciNotation(base=10.0, labelOnlyBase=False)
            _formatter.set_locs(locs=_log_decade_ticklabels)

            ax.xaxis.set_minor_formatter(_formatter)

    def _get_figure(self, figure_name):
        if figure_name not in self._figures:
            self._figures[figure_name] = plt.figure()
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

            for _subplot_dict in _fig_cfg['subplots']:
                for _k, _v in _subplot_dict.iteritems():
                    if isinstance(_v, str):
                        _subplot_dict[_k] = _v.format(**context)
                    elif isinstance(_v, ConfigurationEntry):
                        _subplot_dict[_k] = _v.get(context)

            self._plot_figure(_fig_cfg)

    def _request_all_expressions_with_context(self, context):
        _reqs = []
        for _fig_cfg in self._config['figures']:
            for _subplot_dict in _fig_cfg['subplots']:
                 #_reqs.append(dict(object_spec=_subplot_dict['expression'].format(**context)))
                self._input_controller._request_all_objects_in_expression(_subplot_dict['expression'].format(**context))

        #self._input_controller.request(_reqs)

    def _plot_figure(self, plot_config):

        _mplrc()

        _filename = os.path.join(self._output_folder, plot_config['filename'])

        _fig = self._get_figure(_filename)
        _ax = _fig.gca()

        _stack_bottoms = {}

        # step 2: retrieve data and plot

        for _pc in plot_config['subplots']:
            _kwargs = deepcopy(_pc)

            _expression = _kwargs.pop('expression')
            print("PLT {}".format(_expression))
            _plot_data = self._input_controller.get_expr(_expression)

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
                _kwargs['width'] = 2 * _plot_data['xerr']
                _kwargs.setdefault('align', 'center')
                _kwargs.setdefault('edgecolor', '')
                _kwargs['y'] = _plot_data['y']
                _kwargs['bottom'] = _y_bottom
            else:
                _kwargs['y'] = _plot_data['y'] + _y_bottom
                _kwargs['xerr'] = _plot_data['xerr']

            _show_yerr = _kwargs.pop('show_yerr', True)
            if _show_yerr:
                _kwargs['yerr'] = _plot_data['yerr']

            _y_data = _kwargs.pop('y')
            _normflag = _kwargs.pop('normalize_to_width', False)
            if _normflag:
                _y_data /= 2 * _plot_data['xerr']
                if 'yerr' in _kwargs:
                    _kwargs['yerr'] /= 2 * _plot_data['xerr']

            # run the plot method
            _plot_method(
                _plot_data['x'],
                _y_data,
                **_kwargs
            )

            # update stack bottoms
            if _stack_name is not None:
                _stack_bottoms[_stack_name] += _plot_data['y']

        # step 3: figure adjustments

        # simple axes adjustments
        for _prop_name, _meth_dict in self._PC_KEYS_MPL_AXES_METHODS.iteritems():
            _prop_val = plot_config.get(_prop_name, None)
            if _prop_val is not None:
                getattr(_ax, _meth_dict['method'])(_prop_val, **_meth_dict.get('kwargs', {}))

        # step 4: save figures
        self._close_plot(_ax, plot_config)
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
            self._request_all_expressions_with_context(_expansion_context)

        # second: actual plotting
        for _expansion_context in list(product_dict(**self._config['expansions'])):
            self._run_with_context(_expansion_context)
