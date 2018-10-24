import numpy as np

from copy import deepcopy


class Quantity(object):

    __slots__ = ('_dict',)

    def __init__(self, name, expression, binning):
        self._dict = dict(
            name=name,
            expression=expression,
            binning=binning,
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
        return self._dict['binning']

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


def apply_defines(data_frame, defines):
    """Applies all 'Defines' specified in a dictionary to an data frame."""
    _df = data_frame
    for _k, _v in defines.iteritems():
        try:
            _df = _df.Define(_k, _v)
        except Exception as _e:
            print "[apply_defines] WARNING: Error defining quantity '{}': {}".format(_k, _e)

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
