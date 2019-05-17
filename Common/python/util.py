import os
import re

from contextlib import contextmanager


__all__ = ['CMSSW_VERSION', 'get_cmssw_version', 'report_new_attributes']

_re_numeric = re.compile('[^0-9_]+')


def get_cmssw_version(version_string=os.environ["CMSSW_VERSION"]):
    # strip CMSSW prefix
    if version_string.startswith('CMSSW_'):
        version_string = version_string[6:]
    # split by underscore
    version_tuple = version_string.split('_', 3);
    # remove non-numeric characters
    version_tuple = list(map(lambda s: _re_numeric.sub('', s), version_tuple))
    # cast elems to int or None if failed
    version_tuple = list(map(lambda s: int(s) if len(s) else None, version_tuple))

    return tuple(version_tuple)

@contextmanager
def report_new_attributes(obj, report_label):
    _attr_set = set(obj.__dict__)
    yield
    _attr_set = set(obj.__dict__) - _attr_set

    print("[{}] The following new attributes were added:".format(report_label))
    for _attr in sorted(_attr_set):
        print("\t{}".format(_attr))


CMSSW_VERSION = get_cmssw_version()
