from __future__ import print_function

import abc
import ast
import json
import six
import warnings
import ROOT

from copy import deepcopy
from tqdm import tqdm

import numpy as np

from .._input import InputROOT
from .._lazy import LazyNodeBase, lazify, String
from .._colormaps import viridis
from .._util import make_directory, product_dict

__all__ = ['ContextValue', 'LiteralString', 'InputValue']


class ConfigurationError(Exception):
    pass


class _ContextResolutionError(Exception):
    '''For internal use. Raised when context-sensitive replacement fails at an arbitrary nesting
    level in the config. Reraised at all above levels to reconstruct the evaluation path. Finally
    cast to a ConfigurationError when reraised from the top config level.'''

    def __init__(self, path=None, spec=None, context=None, underlying_error=None):
        self.path = path or tuple()
        self.spec = spec
        self.context = context
        self.underlying_error = underlying_error

    @classmethod
    def from_other(cls, other, new_path=None):
        '''return new instance with data copied from a caught _ContextResolutionError'''
        return cls(
            path=new_path or other.path,
            spec=other.spec,
            context=other.context,
            underlying_error=other.underlying_error
        )

    def __str__(self):
        return (
            "Error resolving placeholders for context value at config path '{path}'."
            "{maybe_context}{maybe_spec}{maybe_underlying_message}"
        ).format(
            self=self,
            path='/'.join('{}'.format(_elem) for _elem in self.path),
            maybe_spec=(
                "\n\nThe context value specification was: {}".format(
                    # default to pretty-printed repr (for LazyNodes), if available
                    getattr(self.spec, '_get_repr', lambda self, **kwargs: repr(self))(pprint=True)
                )
                if self.spec is not None else ''
            ),
            maybe_underlying_message=(
                "\n\nEncountered {}: {}".format(
                    self.underlying_error.__class__.__name__, self.underlying_error
                )
                if self.underlying_error is not None else ''
            ),
            maybe_context=(
                "\n\nThe evaluation context was:\n{}".format(
                    json.dumps(
                        {
                            _k: _v
                            for _k, _v in self.context.items()
                            if not _k.startswith('_')
                        },
                        indent=2,
                        default=lambda obj: repr(obj)
                    )
                )
                if self.context is not None else ''
            )
        )


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
            raise ConfigurationError("Key '{}' not found when dispatching expression '{}' over context.".format(e.args[0], _spec))
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
                try:
                    var[_k] = _ProcessorBase._resolve_context(_v, context)
                except _ContextResolutionError as e:
                    _new_e = _ContextResolutionError.from_other(e, new_path=e.path + (_k,))
                    six.raise_from(_new_e, e)

        elif isinstance(var, list):
            # thread over lists
            for _idx, _v in enumerate(var):
                try:
                    var[_idx] = _ProcessorBase._resolve_context(_v, context)
                except _ContextResolutionError as e:
                    _new_e = _ContextResolutionError.from_other(e, new_path=e.path + (_idx,))
                    six.raise_from(_new_e, e)

        elif isinstance(var, str):
            # replace within string using 'format'
            try:
                return var.format(**context)
            except Exception as e:
                _new_e = _ContextResolutionError(underlying_error=e, spec=var, context=context)
                six.raise_from(_new_e, e)

        elif isinstance(var, LazyNodeBase):
            try:
                return var.eval(context)
            except Exception as e:
                _new_e = _ContextResolutionError(underlying_error=e, spec=var, context=context)
                six.raise_from(_new_e, e)

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
                try:
                    _config[_subkey_for_context_replacing] = _ProcessorBase._resolve_context(_config[_subkey_for_context_replacing], context)
                except _ContextResolutionError as e:
                    _new_e = _ContextResolutionError.from_other(e, new_path=(_subkey_for_context_replacing,) + e.path)
                    six.raise_from(_new_e, e)

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

        # Disable graphical output of ROOT
        ROOT.gROOT.SetBatch(True)

        # -- run over cross product of expansion

        # go through each configured action
        for _action_method in self._ACTIONS:
            # run the action once for each expansion context
            _expansion_contexts = list(product_dict(**self._config[self.CONFIG_KEY_FOR_CONTEXTS]))
            for _expansion_context in (tqdm(_expansion_contexts) if show_progress else _expansion_contexts):
                try:
                    self._run_with_context(_action_method, _expansion_context)
                except _ContextResolutionError as e:
                    # "cast" internal _ContextResolutionError to ConfigurationError before raising
                    six.raise_from(ConfigurationError(str(e)), e)
