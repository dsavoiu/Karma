from __future__ import print_function

import numpy as np

from copy import deepcopy


class Quantity(object):

    __slots__ = ('_dict',)

    def __init__(self, name, expression, binning, named_binnings=None):
        self._dict = dict(
            name=name,
            expression=expression,
            binning=binning,
            named_binnings=named_binnings,
        )

    def __repr__(self):
        return "{}({})".format(
            self.__class__.name,
            ", ".join(["{}={}".format(_k, repr(_v)) for _k, _v in self._dict.iteritems()])
        )

    @property
    def range(self):
        return (self.binning[0], self.binning[-1])

    @property
    def binning(self):
        """The default binning for this quantity. Always defined, even if no special "named binnings" are not."""
        return self._dict['binning']

    @property
    def named_binnings(self):
        """Named binnings defined for this quantity."""
        return self._dict['named_binnings']

    @property
    def expression(self):
        return self._dict['expression']

    @property
    def name(self):
        return self._dict['name']

    def clone(self, **kwargs):
        """Create a clone of quantity, replacing properties as specified by the keyword arguments."""
        _self_dict_copy = deepcopy(self._dict)
        _self_dict_copy.update(kwargs)
        return Quantity(**_self_dict_copy)

    @property
    def named_binning_keys(self):
        """Splitting keys for which named binnings have been defined for this quantity."""
        _nb = self._dict.get('named_binnings', None)
        if _nb is None:
            return None
        return _nb.keys()

    def iter_bins(self, indices=slice(None)):
        """Generator function. Yields tuple (lo, hi) of bin edges for each bin. A subset may be obtained by providing a list of indices or a `slice` object."""
        if isinstance(indices, slice):
            # can use `slice` object for indexing binnings directly
            _iter_pairs = zip(self._dict['binning'][:-1][indices], self._dict['binning'][1:][indices])
        else:
            # use list comrehensions to iteratr over a subset bins with explicitly given `indices`
            _iter_pairs = zip(
                [self._dict['binning'][:-1][_i] for _i in indices],
                [self._dict['binning'][1:][_i]  for _i in indices])

        for _lo, _hi in _iter_pairs:
            yield (_lo, _hi)

    def get_named_binning(self, key, value):
        """Retrieve a binning (if defined) for the case where the splitting key `key` has value `value`. If none defined, return `None`."""
        _nb = self._dict.get('named_binnings', None)
        if _nb is None:
            return None
        _nb = _nb.get(key, None)
        if _nb is None:
            return None
        _nb = _nb.get(value, None)
        return _nb


def apply_defines(data_frame, defines):
    """Applies all 'Defines' specified in a dictionary to an data frame."""
    _df = data_frame
    for _k, _v in defines.iteritems():
        print("[apply_defines] Defining quantity '{}': {}".format(_k, _v))
        try:
            _df = _df.Define(_k, _v)
        except Exception as _e:
            print("[apply_defines] WARNING: Error defining quantity '{}': {}".format(_k, _e))

    return _df


def apply_filters(data_frame, filters):
    """Applies all 'Filters' specified in a list to an data frame."""
    _df = data_frame
    for _filter_expr in filters:
        _df = _df.Filter(_filter_expr)

    return _df


def define_quantities(data_frame, quantities):
    """Define aliases for quantity expressions as specified in dictionary `quantities`."""
    _define_dict = {}  # map of quantities by unique name
    for _q_key, _q in quantities.iteritems():

        # skip quantities with identical names and expressions (can get by name without Define)
        if _q.name == _q.expression:
            continue

        # check if a definition already exists for this name
        if _q.name in _define_dict:
            _orig_def = _define_dict[_q.name]
            raise ValueError("Redefinition of quantity '{}' from '{}' to '{}'".format(_q.name, _orig_def, _q.expression))

        _define_dict[_q.name] = _q.expression

    _df = apply_defines(data_frame, _define_dict)

    return _df
