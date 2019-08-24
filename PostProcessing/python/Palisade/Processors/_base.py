from __future__ import print_function

import abc
import ast
import itertools
import os
import six
import warnings

from copy import deepcopy
from tqdm import tqdm

import numpy as np

from .._input import InputROOT
from .._lazy import LazyNodeBase, lazify, String
from .._colormaps import viridis

__all__ = ['ContextValue', 'LiteralString', 'InputValue']


def _make_directory(dir_path):
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno == 17:  # File exists
            pass
        else:
            raise

def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))


class ConfigurationError(Exception):
    pass


class ContextValue(LazyNodeBase):
    """Configuration object. Is replaced by the value corresponding to the specification `spec`
    dispatched over the current context."""

    _fields = ('spec',)

    def __init__(self, spec):
        LazyNodeBase.__init__(self, spec)

    @staticmethod
    def _eval(node, context):
        """Evaluate an AST node"""
        if isinstance(node, ast.Str): # <string> : simple lookup
            return context[node.s]

        elif isinstance(node, ast.Name): # <identifier> : same treatment as string
            return context[node.id]

        elif isinstance(node, ast.Subscript):  # <left>[<right>]

            _lnode = node.value
            _rnode = node.slice.value

            _inner_ctx = ContextValue._eval(_lnode, context)
            return ContextValue._eval(_rnode, _inner_ctx)

        else:
            raise TypeError(type(node).__name__)

    def eval(self, context):
        # interpret path using AST and dispatch with context
        _spec = self._spec.eval(context)
        try:
            return self._eval(ast.parse(_spec, mode='eval').body, context)
        except KeyError as e:
            raise ConfigurationError("Key '{}' not found when dispatching expression '{}' over context: {}".format(e.args[0], _spec, context))
        except TypeError as e:
            raise ConfigurationError("Unsupported node type '{}' encountered in expression '{}'.".format(e.args[0], _spec))



class InputValue(LazyNodeBase):
    """Configuration object. It is replaced by an the result of evaluating
    `expression` as an expression involving input file objects. The expression
    is dispatched over the current expansion context.

    See :py:meth:`~Palisade.InputROOT.get_expr` for more information about
    input expressions.

    .. note::
        The context must provide an input controller (e.g. :py:class:`~Palisade.InputROOT`)
        under the key ``_input_controller``."""

    _fields = ('expression',)

    def __init__(self, expression):
        LazyNodeBase.__init__(self, expression)

    def eval(self, context):
        _expr = self._expression.eval().format(**context)
        return context['_input_controller'].get_expr(_expr)


# deprecated: keep for backwards compatibility
class LiteralString(String):
    def __init__(self, s):
        """Deprecated. Equivalent to :py:class:`~Palisade.String`."""

        # issue DeprecationWarning
        warnings.warn(
            "Class `LiteralString` is deprecated and will be removed in "
            "the future. Use the equivalent `String` class as a drop-in "
            "replacement.", DeprecationWarning)

        String.__init__(self, s)


class _ProcessorBase(object):
    """Abstract base class from which all processors inherit."""
    __metaclass__ = abc.ABCMeta

    SUBKEYS_FOR_CONTEXT_REPLACING = None
    CONFIG_KEY_FOR_TEMPLATES = None  # 'figures'
    CONFIG_KEY_FOR_CONTEXTS = None # 'expansions'

    _ACTIONS = []

    def __init__(self, config, output_folder):
        """Initialize the processor.

        Parameters
        ----------

            config : `dict`
                processor configuration
            output_folder : `str`
                directory in which to place the output files produced by this task
        """
        self._config = config
        self._output_folder = output_folder


    @staticmethod
    def _resolve_context(var, context):
        '''recursively replace string templates and ``LazyNodeBase`` with contextual values'''
        if isinstance(var, dict):
            # thread over dictionaries
            for _k, _v in six.iteritems(var):
                var[_k] = _ProcessorBase._resolve_context(_v, context)
        elif isinstance(var, list):
            # thread over lists
            for _idx, _v in enumerate(var):
                var[_idx] = _ProcessorBase._resolve_context(_v, context)
        elif isinstance(var, str):
            # replace within string using 'format'
            try:
                return var.format(**context)
            except KeyError as e:
                raise ConfigurationError("Key '{}' not found when dispatching expression '{}' over context: {}".format(e.args[0], var, context))

        elif isinstance(var, LazyNodeBase):
            return var.eval(context)
        else:
            # direct passthrough: no replacement
            pass

        return var


    def _run_with_context(self, action_method, context):
        for _template in self._config[self.CONFIG_KEY_FOR_TEMPLATES]:
            _config = deepcopy(_template)

            # replace context in top-level keys
            for _k, _v in six.iteritems(_config):
                if isinstance(_v, str):
                    _config[_k] = _v.format(**context)
                elif isinstance(_v, LazyNodeBase):
                    _config[_k] = _v.eval(context)

            # replace context only in children of specific subkeys
            for _subkey_for_context_replacing in self.SUBKEYS_FOR_CONTEXT_REPLACING:
                if _subkey_for_context_replacing not in _config:
                    continue
                _config[_subkey_for_context_replacing] = _ProcessorBase._resolve_context(_config[_subkey_for_context_replacing], context)

            try:
                action_method(self, _config)
            except Exception as e:
                print("{} encountered while processing job with config: {}".format(e.__class__.__name__, _config))
                raise

    # -- public API

    def run(self, show_progress=True):
        """Run the processor.

        Parameters
        ----------

            show_progress : `bool`
                if :py:const:`True`, a progress bar will be shown
        """
        # -- run over cross product of expansion

        # go through each configured action
        for _action_method in self._ACTIONS:
            # run the action once for each expansion context
            _expansion_contexts = list(product_dict(**self._config[self.CONFIG_KEY_FOR_CONTEXTS]))
            for _expansion_context in (tqdm(_expansion_contexts) if show_progress else _expansion_contexts):
                self._run_with_context(_action_method, _expansion_context)

