import ast
import collections
import ROOT
import numpy as np
import operator as op
import os
import pandas as pd
import uuid

from array import array

from rootpy import asrootpy
from rootpy.io import root_open
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase


__all__ = ['InputROOTFile', 'InputROOT']


class _ROOTObjectFunctions(object):

    @staticmethod
    def _project_or_clone(tobject, projection_options=None):

        if isinstance(tobject, _ProfileBase):
            # create an "x-projection" with a unique suffix
            if projection_options is None:
                return asrootpy(tobject.ProjectionX(uuid.uuid4().get_hex()))
            else:
                return asrootpy(tobject.ProjectionX(uuid.uuid4().get_hex(), projection_options))
        else:
            return tobject.Clone()

    @staticmethod
    def histdivide(tobject_1, tobject_2, option=""):
        """divide two histograms, taking error calculation option into account"""

        _new_tobject_1 = _ROOTObjectFunctions._project_or_clone(tobject_1)
        _new_tobject_2 = _ROOTObjectFunctions._project_or_clone(tobject_2)

        _new_tobject_1.Divide(_new_tobject_1, _new_tobject_2, 1, 1, option)

        return _new_tobject_1

    @staticmethod
    def efficiency(tobject_numerator, tobject_denominator):
        """Compute TEfficiency"""

        return Efficiency(tobject_numerator, tobject_denominator)

    @staticmethod
    def project_x(tobject):
        """Apply ProjectionX() operation."""

        if hasattr(tobject, 'ProjectionX'):
            _new_tobject = asrootpy(tobject.ProjectionX())
        else:
            print "[INFO] `project_x` not available for object with type {}".format(type(tobject))
            return tobject

        return _new_tobject

    @staticmethod
    def yerr(tobject):
        """replace bin value with bin error and set bin error to zero"""

        # project preserving errors
        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject, "e")

        for _bin_proxy in _new_tobject:
            _bin_proxy.value, _bin_proxy.error = _bin_proxy.error, 0

        return _new_tobject

    @staticmethod
    def atleast(tobject, min_value):
        """mask all values below threshold"""

        # project preserving errors
        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject, "e")

        for _bin_proxy in _new_tobject:
            if _bin_proxy.value < min_value:
                _bin_proxy.value, _bin_proxy.error = 0, 0

        return _new_tobject

    @staticmethod
    def threshold(tobject, min_value):
        """returns a histogram like tobject with bins set to zero if the fall below the miminum value and to one if not. Errors are always set to zero"""

        # project preserving errors
        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject)

        for _bin_proxy in _new_tobject:
            if _bin_proxy.value < min_value:
                _bin_proxy.value, _bin_proxy.error = 0, 0
            else:
                _bin_proxy.value, _bin_proxy.error = 1, 0

        return _new_tobject

    @staticmethod
    def discard_errors(tobject):
        """set all bin errors to zero"""

        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject)

        for _bin_proxy in _new_tobject:
            _bin_proxy.error = 0

        return _new_tobject

    @staticmethod
    def bin_width(tobject):
        """replace bin value with width of bin and set bin error to zero"""

        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject)

        for _bin_proxy in _new_tobject:
            _bin_proxy.value, _bin_proxy.error = _bin_proxy.x.width, 0

        return _new_tobject

    @staticmethod
    def max(*tobjects):
        """binwise `max` for a collection of histograms with identical binning"""

        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobjects[0], "e")

        _tobj_clones = []
        for _tobj in tobjects:
            _tobj_clones.append(_ROOTObjectFunctions._project_or_clone(_tobj, "e"))

        for _bin_proxies in zip(_new_tobject, *_tobj_clones):
            _argmax = max(range(1, len(_bin_proxies)), key=lambda idx: _bin_proxies[idx].value)
            _bin_proxies[0].value = _bin_proxies[_argmax].value
            _bin_proxies[0].error = _bin_proxies[_argmax].error

        # cleanup
        for _tobj_clone in _tobj_clones:
            _tobj_clone.Delete()

        return _new_tobject

    @staticmethod
    def mask_if_less(tobject, tobject_ref):
        """set `tobject` bins and their errors to zero if their content is less than the value in `tobject_ref`"""

        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject, "e")
        _new_tobject_ref = _ROOTObjectFunctions._project_or_clone(tobject_ref, "e")

        for _bin_proxy, _bin_proxy_ref in zip(_new_tobject, _new_tobject_ref):
            if _bin_proxy.value < _bin_proxy_ref.value:
                _bin_proxy.value, _bin_proxy.error = 0, 0

        # cleanup
        _new_tobject_ref.Delete()

        return _new_tobject

    @staticmethod
    def threshold_by_ref(tobject, tobject_ref):
        """set `tobject` bins to zero if their content is less than the value in `tobject_ref`, and to 1 otherwise. Result bin errors are always set to zero."""

        _new_tobject = _ROOTObjectFunctions._project_or_clone(tobject)
        _new_tobject_ref = _ROOTObjectFunctions._project_or_clone(tobject_ref)

        for _bin_proxy, _bin_proxy_ref in zip(_new_tobject, _new_tobject_ref):
            if _bin_proxy.value < _bin_proxy_ref.value:
                _bin_proxy.value, _bin_proxy.error = 0, 0
            else:
                _bin_proxy.value, _bin_proxy.error = 1, 0

        # cleanup
        _new_tobject_ref.Delete()

        return _new_tobject


class InputROOTFile(object):
    """An input module for accessing objects from a single ROOT file.

    Multiple objects can be requested. They will be all be retrieved
    simultaneously and cached on the first subsequent call to `get()`.
    The file will thus only be opened once.

    Usage example
    -------------
        m = InputROOTFile('/path/to/rootfile.root')

        m.request(dict(object_path='MyDirectory/myObject'))
        my_object = m.get('MyDirectory/myObject')
    """

    def __init__(self, filename):
        self._filename = filename
        self._outstanding_requests = dict()
        self._plot_data_cache = dict()

    def _process_outstanding_requests(self):
        # if no requests, return immediately
        if not self._outstanding_requests:
            return

        # process outstanding requests
        with root_open(self._filename) as _tfile:
            for tobj_path, request_spec in self._outstanding_requests.iteritems():
                _rebin_factor = request_spec.pop('rebin_factor', None)
                _profile_error_option = request_spec.pop('profile_error_option', None)

                _tobj = _tfile.Get(tobj_path)
                _tobj.SetDirectory(0)
                print tobj_path, _tobj

                # aply rebinning (if requested)
                if _rebin_factor is not None:
                    _tobj.Rebin(_rebin_factor)

                # set TProfile error option (if requested)
                if _profile_error_option is not None:
                    # TOOD: check if profile?
                    _tobj.SetErrorOption(_profile_error_option)

                self._plot_data_cache[tobj_path] = _tobj

        self._outstanding_requests = dict()


    def get(self, object_path):
        """
        Get an object.

        Parameters
        ----------
            object_path : string, path to resource in ROOT file (e.g. "directory/object")
        """
        # request object if not present
        if object_path not in self._outstanding_requests:
            if object_path not in self._plot_data_cache:
                self.request([dict(object_path=object_path)])

        # process request if object is waiting
        if object_path in self._outstanding_requests:
            self._process_outstanding_requests()

        # return object
        return self._plot_data_cache[object_path]

    def request(self, request_specs):
        """
        Request an object. Requested objects are all retrieved in one
        go when one of them is retrived via 'get()'

        Parameters
        ----------
            request_specs : e.g. dict(object_path="directory/object")
        """
        for request_spec in request_specs:
            _object_path = request_spec.pop('object_path')
            _force_rerequest = request_spec.pop('force_rerequest', True)

            # override earlier request iff 'force_rerequest' is True
            if (not (_object_path in self._outstanding_requests or _object_path in self._plot_data_cache)) or _force_rerequest:
                self._outstanding_requests[_object_path] = request_spec

                if _object_path in self._plot_data_cache:
                    del self._plot_data_cache[_object_path]

    def clear(self):
        """
        Remove all cached data and outstanding requests.
        """
        self._plot_data_cache = {}
        self._outstanding_requests = {}



class InputROOT(object):
    """An input module for accessing objects from multiple ROOT files.

    A nickname can be registered for each file, which then allows
    object retrieval by prefixing it to the object path
    (i.e. '<file_nickname>:<object_path_in_file>').

    Single-file functionality is delegated to child `InputROOTFile` objects.

    Usage example
    -------------
        m = InputROOT()
        m.add_file('/path/to/rootfile.root', nickname='file0')

        m.request(dict(file_nickname='file0', object_path='MyDirectory/myObject'))
        my_object = m.get('file0', 'MyDirectory/myObject')
    """


    operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.BitXor: op.xor,
        ast.USub: op.neg
    }

    # functions which can be applied to ROOT objects
    functions = {
        'yerr':                     _ROOTObjectFunctions.yerr,
        'bin_width':                _ROOTObjectFunctions.bin_width,
        'project_x':                _ROOTObjectFunctions.project_x,
        'h':                        _ROOTObjectFunctions.project_x,  # alias
        'hist':                     _ROOTObjectFunctions.project_x,  # alias
        'divide':                   _ROOTObjectFunctions.histdivide,
        'discard_errors':           _ROOTObjectFunctions.discard_errors,
        'efficiency':               _ROOTObjectFunctions.efficiency,
        'atleast':                  _ROOTObjectFunctions.atleast,
        'max':                      _ROOTObjectFunctions.max,
        'mask_if_less':             _ROOTObjectFunctions.mask_if_less,
        'threshold':                _ROOTObjectFunctions.threshold,
        'threshold_by_ref':         _ROOTObjectFunctions.threshold_by_ref,
    }

    def __init__(self, files_spec=None):
        """Create the module. A mapping of nicknames to file paths may be specified optionally.

        Parameters
        ----------

            files_spec [optional]: dict specifying file nicknames (keys) and paths pointed to (values)
        """
        self._input_controllers = {}
        self._file_nick_to_realpath = {}
        if files_spec is not None:
            for _nickname, _file_path in files_spec.iteritems():
                self.add_file(_file_path, nickname=_nickname)

    def _get_input_controller_for_file(self, file_spec):
        '''get input controller for file specification. handle nickname resolution'''
        _file_realpath = self._file_nick_to_realpath.get(file_spec, file_spec)
        if _file_realpath not in self._input_controllers:
            raise ValueError("Cannot get input controller for file specification '{}': have you added a file with this nickname or path?".format(file_spec))
        return self._input_controllers[_file_realpath]


    @staticmethod
    def _get_file_nickname_and_obj_path(object_spec):
        _file_nickname, _object_path_in_file = object_spec.split(':', 1)
        return _file_nickname, _object_path_in_file

    def add_file(self, file_path, nickname=None):
        """
        Add a ROOT file.

        Parameters
        ----------
            file_path : string (path to ROOT file)
        """

        # determine real (absolute) path for file
        _file_realpath = os.path.realpath(file_path)

        # register nickname
        if nickname is not None:
            if nickname in self._file_nick_to_realpath:
                raise ValueError("Cannot add file for nickname '{}': nickname already registered for file '{}'".format(nickname, filename))
            self._file_nick_to_realpath[nickname] = _file_realpath
            # also register filename (or relative file path) as alternative nickname
            self._file_nick_to_realpath[file_path] = _file_realpath

        # create controller for file
        if _file_realpath not in self._input_controllers:
            self._input_controllers[_file_realpath] = InputROOTFile(_file_realpath)


    def get(self, object_spec):
        """
        Get an object.

        Parameters
        ----------
            object_spec : string, path to resource in ROOT file (e.g. "file_nickname:directory/object")
        """
        _file_nickname, _object_path_in_file = self._get_file_nickname_and_obj_path(object_spec)
        _ic = self._get_input_controller_for_file(_file_nickname)
        return _ic.get(_object_path_in_file)


    def request(self, request_specs):
        """
        Request an object. Requested objects are all retrieved in one
        go when one of them is retrived via 'get()'

        `request_specs` must be a list of dicts specifying requests for
        objects from files.

        A request dict must have either a key `object_spec`, which contains both the
        file nickname and the path to the object within the file, or two keys
        `file_nickname` and `object_path` specifying these separately.

        The following requests behave identically:
            * dict(file_nickname='file0', object_path="directory/object")
            * dict(object_spec="file0:directory/object")

        Parameters
        ----------
            request_specs : list of dict
        """
        _delegations = {}
        for request_spec in request_specs:
            _file_nickname = request_spec.pop('file_nickname', None)
            _object_path_in_file = request_spec.pop('object_path', None)
            _object_spec = request_spec.pop('object_spec', None)

            if not ((_object_spec is not None) == ((_file_nickname is None) and (_object_path_in_file is None))):
                raise ValueError("Invalid request: must either contain both 'file_nickname' and 'object_path' keys or an 'object_spec' key, but contains: {}".format(request_spec.keys()))

            if _object_spec is not None:
                _file_nickname, _object_path_in_file = self._get_file_nickname_and_obj_path(_object_spec)

            if _file_nickname not in _delegations:
                _delegations[_file_nickname] = []
            _delegations[_file_nickname].append(dict(object_path=_object_path_in_file, **request_spec))

        for _file_nickname, _requests in _delegations.iteritems():
            _ic = self._get_input_controller_for_file(_file_nickname)
            _ic.request(_requests)


    def get_expr(self, expr):
        """
        Perform basic arithmetic on objects and return result
        """
        expr = expr.strip()   # extraneous spaces otherwise interpreted as indentation
        self._request_all_objects_in_expression(expr)
        return self._eval(node=ast.parse(expr, mode='eval').body, operators=self.operators, functions=self.functions)

    def _request_all_objects_in_expression(self, expr, **other_request_params):
        """Walk through the expression AST and request an object for each string or identifier"""
        _ast = ast.parse(expr, mode='eval')
        _reqs = []
        for _node in ast.walk(_ast):
            if isinstance(_node, ast.Name):
                _obj_spec = _node.id
            elif isinstance(_node, ast.Str):
                _obj_spec = _node.s
            else:
                continue

            if ':' in _obj_spec:
                _reqs.append(dict(object_spec=_obj_spec, force_rerequest=False, **other_request_params))
        self.request(_reqs)

    def _eval(self, node, operators, functions):
        """Evaluate an AST node"""
        if isinstance(node, ast.Name): # <string> : array column
            #print 'Encountered node of type ast.Name: %s' % (node.id,)
            return self.get(node.id)
        elif isinstance(node, ast.Str): # <string> : array column
            return self.get(node.s)
        elif isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.Call): # node names containing parentheses (interpreted as 'Call' objects)
            return functions[node.func.id](*map(lambda _arg: self._eval(_arg, operators, functions), node.args))
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return operators[type(node.op)](self._eval(node.left, operators, functions), self._eval(node.right, operators, functions))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return operators[type(node.op)](self._eval(node.operand, operators, functions))
        else:
            raise TypeError(node)
