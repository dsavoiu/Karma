from __future__ import print_function

import errno
import itertools
import os


def make_directory(dir_path, exist_ok=False):
    """Convenience wrapper around os.makedirs, with option to run successfully if the targer directory exists"""
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if exist_ok and e.errno == errno.EEXIST:  # file exists
            pass
        else:
            raise

def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))


def group_by(iterable, n):
    '''Return list of iterables of elements of `iterable`, grouped in batches of at most `n`'''
    _l = len(iterable)
    _n_groups = _l//n + (_l%n>0)
    _grouped_iterable = [iterable[_i*n:min(_l,(_i+1)*n)] for _i in range(_n_groups)]
    return _grouped_iterable

