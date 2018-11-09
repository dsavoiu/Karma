import abc
import ast
import itertools
import os

from copy import deepcopy
from tqdm import tqdm

import numpy as np

from .._input import InputROOT
from .._colormaps import viridis

__all__ = ['ContextValue', 'LiteralString']


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


class _ProcessorBase(object):
    """Abstract base class from which all processors inherit."""
    __metaclass__ = abc.ABCMeta

    SUBKEYS_FOR_CONTEXT_REPLACING = None
    CONFIG_KEY_FOR_TEMPLATES = None  # 'figures'
    CONFIG_KEY_FOR_CONTEXTS = None # 'expansions'

    _ACTIONS = []

    def __init__(self, config, output_folder):
        self._config = config
        self._output_folder = output_folder

    def _run_with_context(self, action_method, context):
        for _template in self._config[self.CONFIG_KEY_FOR_TEMPLATES]:
            _config = deepcopy(_template)

            for _k, _v in _config.iteritems():
                if isinstance(_v, str):
                    _config[_k] = _v.format(**context)
                elif isinstance(_v, ConfigurationEntry):
                    _config[_k] = _v.get(context)

            for _subkey_for_context_replacing in self.SUBKEYS_FOR_CONTEXT_REPLACING:
                if _subkey_for_context_replacing not in _config:
                    continue
                for _dict_for_subkey in _config[_subkey_for_context_replacing]:
                    for _k, _v in _dict_for_subkey.iteritems():
                        if isinstance(_v, str):
                            _dict_for_subkey[_k] = _v.format(**context)
                        elif isinstance(_v, ConfigurationEntry):
                            _dict_for_subkey[_k] = _v.get(context)

            action_method(self, _config)

    # -- public API

    def run(self):
        # -- run over cross product of expansion

        # go through each configured action
        for _action_method in self._ACTIONS:
            # run the action once for each expansion context
            for _expansion_context in tqdm(list(product_dict(**self._config[self.CONFIG_KEY_FOR_CONTEXTS]))):
                self._run_with_context(_action_method, _expansion_context)

