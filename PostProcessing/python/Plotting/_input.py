import ast
import ROOT
import numpy as np
import operator as op
import os
import pandas as pd
import uuid

from array import array


__all__ = ['InputROOTFile', 'InputROOT']


class _PlotData(object):
    def __init__(self, plot_data_dict):
        self._dict = plot_data_dict

    @classmethod
    def from_kwargs(cls, **kwargs):
        return cls(plot_data_dict=kwargs)

    # -- delegate to dict

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def update(self, *args, **kwargs):
        return self._dict.update(*args, **kwargs)

    def __getattr__(self, attr_name):
        if attr_name in self._dict:
            return self._dict[attr_name]
        return self.__dict__[attr_name]

    # -- implement addition, subtraction, division, etc.
    def __add__(self, other):
        if isinstance(other, self.__class__):
            assert(np.allclose(self.x, other.x))
            assert(np.allclose(self.xerr, other.xerr))
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.add(self.y, other.y),
                xerr=self.xerr,
                yerr=np.sqrt(self.yerr**2 + other.yerr**2),  # ignore other errors
            )
        else:
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.add(self.y, other),
                xerr=self.xerr,
                yerr=self.yerr,
            )

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            assert(np.allclose(self.x, other.x))
            assert(np.allclose(self.xerr, other.xerr))
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.sub(self.y, other.y),
                xerr=self.xerr,
                yerr=op.sub(self.yerr, other.y),  # ignore denom errors
            )
        else:
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.sub(self.y, other),
                xerr=self.xerr,
                yerr=self.yerr,  # scalar subtraction has no effect on errors
            )

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            assert(np.allclose(self.x, other.x))
            assert(np.allclose(self.xerr, other.xerr))
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.mul(self.y, other.y),
                xerr=self.xerr,
                yerr=op.mul(self.yerr, other.y),  # ignore other errors
            )
        else:
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.mul(self.y, other),
                xerr=self.xerr,
                yerr=op.mul(self.yerr, other),
            )

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            assert(np.allclose(self.x, other.x))
            assert(np.allclose(self.xerr, other.xerr))
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.truediv(self.y, other.y),
                xerr=self.xerr,
                yerr=op.truediv(self.yerr, other.y),  # ignore denom errors
            )
        else:
            return self.__class__.from_kwargs(
                x=self.x,
                y=op.truediv(self.y, other),
                xerr=self.xerr,
                yerr=op.truediv(self.yerr, other),
            )

    def __radd__(self, other):
        # = other + self
        return self + other

    def __rsub__(self, other):
        # = other - self
        return self.__class__.from_kwargs(
            x=self.x,
            y=op.sub(other, self.y),
            xerr=self.xerr,
            yerr=self.yerr,
        )

    def __rmul__(self, other):
        # = other * self
        return self * other

    def __rtruediv__(self, other):
        # = other / self
        return self.__class__.from_kwargs(
            x=self.x,
            y=op.truediv(other, self.y),
            xerr=self.xerr,
            yerr=op.truediv(self.yerr, self.y**2),  # error propagation
        )

    def __str__(self):
        return str(self._dict)

    def __repr__(self):
        return repr(self._dict)

# def nansum(*pds):
#     if not pds:
#         return None
#     for _pd in pds:
#         assert isinstance(_pd, _PlotData)
#         assert(np.allclose(pds[0].x, _pd.x))
#         assert(np.allclose(pds[0].xerr, _pd.xerr))
#     return _PlotData.from_kwargs(
#         x=pds[0].x,
#         y=np.nansum(pd_a.y, pd_b.y),
#         xerr=pds[0].xerr,
#         yerr=np.sqrt(pd_a.yerr**2 + pd_b.yerr**2),  # ignore pd_b errors
#     )


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
        _tfile = ROOT.TFile(self._filename)
        for tobj_path, request_spec in self._outstanding_requests.iteritems():
            _rebin_factor = request_spec.pop('rebin_factor', None)

            _tobj = _tfile.Get(tobj_path)

            # "cast" TProfile to TH1D
            if type(_tobj) is ROOT.TProfile:
                _tobj_name = tobj_path.split('/')[-1]
                _tobj = _tobj.ProjectionX("{}_px_{}".format(_tobj_name, uuid.uuid4()))

            # check if object exists and is of plottable type
            if type(_tobj) is ROOT.TObject:
                raise ValueError("Cannot get TH1D '{}': object does not exist!'".format(tobj_path))
            if type(_tobj) is not ROOT.TH1D:
                raise ValueError("Cannot get TH1D '{}': object exists but is of different type '{}'".format(tobj_path, type(_tobj)))

            # aply rebinning (if requested)
            if _rebin_factor is not None:
                _tobj.Rebin(_rebin_factor)

            # handle TH1D
            _nbins = _tobj.GetNbinsX()
            _buf = _tobj.GetArray()
            _y = np.frombuffer(_buf, 'd', _nbins, 8)
            _xlo = np.array([_tobj.GetXaxis().GetBinLowEdge(i) for i in range(1, _nbins+1)])
            _xup = np.array([_tobj.GetXaxis().GetBinUpEdge(i) for i in range(1, _nbins+1)])

            _yerr_up = [_tobj.GetBinErrorUp(i) for i in range(1, _nbins+1)]
            _yerr_dn = [_tobj.GetBinErrorLow(i) for i in range(1, _nbins+1)]
            _yerr = np.array([_yerr_dn, _yerr_up])

            _xcen = 0.5 * (_xup + _xlo)
            _xerr = 0.5 * (_xup - _xlo)

            self._plot_data_cache[tobj_path] = _PlotData.from_kwargs(
                x=_xcen.astype(float),
                y=_y.astype(float),
                xerr=_xerr.astype(float),
                yerr=_yerr.astype(float),
                rebin_factor=_rebin_factor,
            )

        _tfile.Close()
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
            self._outstanding_requests[_object_path] = request_spec
            if _object_path in self._plot_data_cache:
                del self._plot_data_cache[_object_path]


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

    functions = {
        'nanguard_zero': lambda pd: _PlotData.from_kwargs(**{k : np.where(np.isnan(v), 0, v) for k, v in pd._dict.iteritems()}),
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
            for _nickname, _filepath in files_spec.iteritems():
                self.add_file(_filepath, nickname=_nickname)

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
            file_path : string, path to ROOT file
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
            _file_nickname = request_spec.get('file_nickname', None)
            _object_path_in_file = request_spec.get('object_path', None)
            _object_spec = request_spec.get('object_spec', None)

            if not ((_object_spec is not None) == ((_file_nickname is None) and (_object_path_in_file is None))):
                raise ValueError("Invalid request: must either contain both 'file_nickname' and 'object_path' keys or an 'object_spec' key, but contains: {}".format(request_spec.keys()))

            if _object_spec is not None:
                _file_nickname, _object_path_in_file = self._get_file_nickname_and_obj_path(_object_spec)

            if _file_nickname not in _delegations:
                _delegations[_file_nickname] = []
            _delegations[_file_nickname].append(dict(object_path=_object_path_in_file))

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

    def _request_all_objects_in_expression(self, expr):
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
                _reqs.append(dict(object_spec=_obj_spec))
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
