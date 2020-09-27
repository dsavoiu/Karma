# -*- coding: utf8 -*-
"""Helper classes for lazy evaluation."""

import abc
import ast
import six
import operator

__all__ = [
    'lazify',
    'LazyNodeBase', 'LazyIterableNodeBase',
    'Lazy', 'Map', 'List', 'String', 'FormatString',
    'If', 'Try',
    'BinOp', 'Op', 'Call', 'Attribute']

try:
    # Python 3
    from inspect import Signature, Parameter
except ImportError:
    # Python 2
    from funcsigs import Signature, Parameter

_OPERATORS = {
    # arithmetic
    'add': (operator.add, True),
    'sub': (operator.sub, True),
    'mul': (operator.mul, True),
    'truediv': (operator.truediv, True),
    'floordiv': (operator.floordiv, True),
    'mod': (operator.mod, True),
    # binary arithmetic
    'lshift': (operator.lshift, True),
    'rshift': (operator.rshift, True),
    # logical
    'and': (operator.and_, True),
    'or': (operator.or_, True),
    'xor': (operator.xor, True),
    # comparison
    'eq': (operator.eq, False),
    'ne': (operator.ne, False),
    'lt': (operator.lt, False),
    'le': (operator.le, False),
    'gt': (operator.gt, False),
    'ge': (operator.ge, False),
    # other
    'getitem': (operator.getitem, False),
    'contains': (operator.contains, False),
}

_UNARY_OPERATORS = {
    'invert': operator.invert,
    'neg': operator.neg,
    'pos': operator.pos,
}

# 'div' operator only available in Python 2
if six.PY2:
    _OPERATORS['div'] = (operator.div, True)

# '_abs' operator only available in Python 3
if six.PY3:
    _UNARY_OPERATORS['abs'] = operator._abs


def lazify(obj):
    """Convert an object into a lazy version of the object.

    Returns *lazy node* objects unchanged.
    Converts tuples and list into :py:class:`~Palisade.List` objects
    and dicts into :py:class:`~Palisade.Map` objects.
    Wraps everything else in a :py:class:`~Palisade.Lazy` container."""

    if isinstance(obj, LazyNodeBase):
        # pass `LazyNodes` through untouched
        return obj
    elif isinstance(obj, dict):
        # convert dictionaries to `Map`
        return Map(obj)
    elif isinstance(obj, list) or isinstance(obj, tuple):
        # convert lists and tuples to `List`
        return List(obj)
    else:
        # convert everything else to `Lazy`
        return Lazy(obj)


def _add_operators(cls):
    """class decorator for implementing common operator methods for nodes"""

    for name, (op, add_reversed) in list(_OPERATORS.items()):
        setattr(cls, '__{}__'.format(name), cls._make_binop_method(op))
        if add_reversed:
            setattr(cls, '__r{}__'.format(name), cls._make_rbinop_method(op))
    for name, op in _UNARY_OPERATORS.items():
        setattr(cls, '__{}__'.format(name), cls._make_unaryop_method(op))

    return cls


@_add_operators
@six.add_metaclass(abc.ABCMeta)
class LazyNodeBase(object):
    """The abstract base class from which all lazy node objects must inherit."""

    _fields = tuple()

    def __init__(self, *args, **kwargs):
        """Default constructor: parse all arguments as field names and nodes"""
        _nargs = len(args) + len(kwargs)
        if _nargs > len(self.__class__._fields):
            raise TypeError(
                "{}() takes at most {} argument{} but {} were given".format(
                    self.__class__.__name__,
                    len(self.__class__._fields),
                    "" if len(self.__class__._fields) == 1 else "s",
                    _nargs,
                )
            )

        # parse call signature and determine attributes
        _attrs = {}
        for _i, _f in enumerate(self.__class__._fields):
            try:
                _attrs[_f] = kwargs[_f] if _f in kwargs else args[_i]
            except IndexError:
                # argument list too short
                raise TypeError(
                    "{}() missing required argument: '{}'".format(
                        self.__class__.__name__,
                        _f
                    )
                )

        # set attributes
        for _attr, _value in _attrs.items():
            setattr(self, '_'+_attr, lazify(_value))

    __init__.__signature__ = Signature(
        parameters=[
            Parameter(name=_f, kind=Parameter.POSITIONAL_OR_KEYWORD)
            for _f in _fields
        ]
    )

    if six.PY3:
        def __bool__(self):
            """All lazy objects are falsy,"""
            return False
    else:
        def __nonzero__(self):
            """All lazy objects are falsy,"""
            return False

    def __deepcopy__(self, memo):
        """Override deepcopy."""
        # this simplifies the implementation of Processors,
        # but could have unintended consequences
        # TODO: reimplement processors wihout `deepcopy`
        return self

    def __hash__(self):
        """Hash is computed as if the lazy object were a tuple."""
        return tuple.__hash__(tuple(self.__dict__['_'+_f] for _f in self._fields))

    def __getattr__(self, attr):
        """Make a lazy :py:class:`~Palisade.Attribute` node using the current node as the object
        and the supplied argument as the attribute name."""
        return Attribute(
            obj=self,
            attr=lazify(attr))

    def __call__(self, *args, **kwargs):
        """Make a lazy :py:class:`~Palisade.Call` node using the current node as the callable
        and the supplied arguments as the call arguments."""
        return Call(
            func=self,
            args=lazify(args),
            kwargs=lazify(kwargs))

    def _get_repr(self, pprint=False, level=1):
        _prefix = '\n'+level * '  ' if pprint else ''
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join([
                '{}{}={}'.format(
                    _prefix,
                    f,
                    (self.__dict__['_'+f]._get_repr(pprint=pprint, level=level+1)
                     if isinstance(self.__dict__['_'+f], LazyNodeBase)
                     else repr(self.__dict__['_'+f]))
                )
                for f in self.__class__._fields
            ]) + ('\n'+(level-1) * '  ' if pprint and level > 0 else '')
        )

    def __repr__(self):
        return self._get_repr()

    def pprint(self):
        """Pretty-print entire dependency tree for this node."""
        print(self._get_repr(pprint=True, level=1))

    @classmethod
    def _make_binop_method(cls, op):
        def _binop_method(self, other):
            return BinOp(left=self, right=lazify(other), op=op)
        return _binop_method

    @classmethod
    def _make_rbinop_method(cls, op):
        def _rbinop_method(self, other):
            return BinOp(left=lazify(other), right=self, op=op)
        return _rbinop_method

    @classmethod
    def _make_unaryop_method(cls, op):
        def _unaryop_method(self):
            return Op(operand=self, op=op)
        return _unaryop_method

    @abc.abstractmethod
    def eval(self, context=None):
        """Evaluate this node with an optional context."""
        raise NotImplementedError


class LazyIterableNodeBase(LazyNodeBase):
    """Iterable nodes must provide an __iter__ method"""

    @abc.abstractmethod
    def __iter__(self):
        raise NotImplementedError


class Lazy(LazyNodeBase):
    """A lazy container for a single value `value`.
    It will be replaced with the contained value on evaluation.

    Note that :py:class:`~Palisade.Lazy` behaves differently from other lazy
    containers in that it does not call the `eval` method
    of its contained object. If :py:class:`~Palisade.Lazy` is used to contain
    objects derived from *lazy node*, the `eval` method.
    must be called explicitly."""

    _fields = ('value',)

    def __init__(self, value):
        self._value = value

    def _get_repr(self, pprint=False, level=1):
        return '{}({!r})'.format(self.__class__.__name__, self._value)

    def eval(self, context=None):
        return self._value


# note: Map implementation differs from 'dict':
# stores keys and values in two coordinated lists
#   -> not made iterable for simplicity
class Map(LazyNodeBase):
    """A lazy object that acts as a dict-like container for
    the key-value pairs contained in `mapping`.

    Both the keys and and values stored in `mapping` should
    be lazy objects. They will be evaluated when the enclosing
    :py:class:`~Palisade.Map` is evaluated.

    Constructing a :py:class:`~Palisade.Map` with keys or values not derived from
    a *lazy node* class will cause these to be wrapped
    inside a :py:class:`~Palisade.Lazy` container."""

    _fields = ('keys', 'values')

    def __init__(self, mapping):
        self._keys = list(map(lazify, mapping.keys()))
        self._values = list(map(lazify, mapping.values()))

    def _get_repr(self, pprint=False, level=1):
        _prefix = '\n'+level * '  ' if pprint else ''
        return '{}({{{}}})'.format(
            self.__class__.__name__,
            ', '.join([
                '{}{} : {}'.format(
                    _prefix,
                    (_k._get_repr(pprint=pprint, level=level+1)
                     if isinstance(_k, LazyNodeBase)
                     else repr(_k)),
                    (_v._get_repr(pprint=pprint, level=level+1)
                     if isinstance(_v, LazyNodeBase)
                     else repr(_v))
                )
                for _k, _v in zip(self._keys, self._values)
            ]) + ('\n'+(level-1) * '  ' if pprint and level > 0 else '')
        )

    def eval(self, context=None):
        return {
            k.eval(context): v.eval(context)
            for k, v in zip(self._keys, self._values)
        }


class List(LazyIterableNodeBase):
    """A lazy object that acts as a list-like container for
    the elements contained in `elts`.

    The elements of `elts` should be lazy objects. They will
    be evaluated when the enclosing :py:class:`~Palisade.List` is evaluated.

    Constructing a :py:class:`~Palisade.List` from objects not derived from
    a *lazy node* class will cause these to be wrapped
    inside a :py:class:`~Palisade.Lazy` container."""

    _fields = ('elts',)

    def __init__(self, elts):
        self._elts = list(map(lazify, elts))

    def _get_repr(self, pprint=False, level=1):
        _prefix = '\n'+level * '  ' if pprint else ''
        return '{}([{}])'.format(
            self.__class__.__name__,
            ', '.join([
                '{}{}'.format(
                    _prefix,
                    (_e._get_repr(pprint=pprint, level=level+1)
                     if isinstance(_e, LazyNodeBase)
                     else repr(_e))
                )
                for _e in self._elts
            ]) + ('\n'+(level-1) * '  ' if pprint and level > 0 else '')
        )

    def __getitem__(self, index):
        return self._elts[index]

    def __iter__(self):
        return iter(self._elts)

    def eval(self, context=None):
        return [el.eval(context) for el in self._elts]


class If(LazyNodeBase):
    """A lazy object that represents a conditional
    expression that evaluates to either `true_value` or
    `false_value` depending on the truth value of the
    condition `condition`.

    The `condition`, `true_value` and `false_value` should
    be lazy objects. They will be evaluated when the `If`
    is evaluated.

    The operator `op` must be a callable that takes
    exactly two positional arguments."""

    _fields = ('condition', 'true_value', 'false_value')

    def __init__(self, condition, true_value, false_value):
        return LazyNodeBase.__init__(self, condition, true_value, false_value)

    def eval(self, context=None):
        if self._condition.eval(context):
            return self._true_value.eval(context)
        else:
            return self._false_value.eval(context)


class Try(LazyNodeBase):
    """A lazy object that represents a try-except
    clause that attempts to evaluate to `value`. If
    an exception is thrown during evaluation, its type
    is it checked against `exception`. If the exception
    is an instance of `exception`, it is caught and
    `value_on_exception` is evaluated and returned,
    otherwise it is raised."""

    _fields = ('value', 'exception', 'value_on_exception')

    def __init__(self, value, exception, value_on_exception):
        return LazyNodeBase.__init__(self, value, exception, value_on_exception)

    def eval(self, context=None):
        try:
            return self._value.eval(context=context)
        except self._exception.eval():
            return self._value_on_exception.eval(context=context)


class BinOp(LazyNodeBase):
    """A lazy object that represents a binary operation `op`
    to be applied to the `left` and `right` operands.

    The operands `left` and `right` should be lazy objects.
    They will be evaluated when the ``BinOp`` is evaluated.

    The operator `op` must be a callable that takes
    exactly two positional arguments."""

    _fields = ('left', 'right', 'op')

    def __init__(self, left, right, op):
        self._left = lazify(left)
        self._right = lazify(right)
        self._op = op

    def eval(self, context=None):
        return self._op(self._left.eval(context),
                        self._right.eval(context))

class Op(LazyNodeBase):
    """A lazy object that represents a unary operation `op`
    to be applied to the operand `operand`.

    The operand `operand` should be a lazy object.
    It will be evaluated when the ``Op`` is evaluated.

    The operator `op` must be a callable that takes
    exactly one positional argument."""

    _fields = ('operand', 'op')

    def __init__(self, operand, op):
        self._operand = lazify(operand)
        self._op = op

    def eval(self, context=None):
        return self._op(self._operand.eval(context))


class Call(LazyNodeBase):
    """A lazy object that represents an invocation of a
    callable `func` with the positional arguments `args`
    and the keyword arguments `kwargs`.

    The function `func` should be a lazy object that evaluates
    to a callable. It will be evaluated when the ``Call``
    is evaluated.

    The arguments `args` and `kwargs` must be lazy objects
    that evaluate to a list and a dictionary, respectively.
    They will be evaluated when the ``Call`` is evaluated
    and will be passed to the evaluated `function` as unpacked
    positional and keyword arguments, respectively."""

    _fields = ('func', 'args', 'kwargs')

    def __init__(self, func, args, kwargs):
        return LazyNodeBase.__init__(self, func, args, kwargs)

    def eval(self, context=None):
        return self._func.eval(context)(*self._args.eval(context), **self._kwargs.eval(context))


class Attribute(LazyNodeBase):
    """A lazy object that represents access to the
    attribute `attr` of the object `obj`.

    The object `obj` and the attribute `attr` should be
    lazy objects that evaluate to an object and a string,
    respectively. They will be evaluated when the `Attribute`
    is evaluated."""

    _fields = ('obj', 'attr')

    def __init__(self, obj, attr):
        return LazyNodeBase.__init__(self, obj, attr)

    def eval(self, context=None):
        return getattr(self._obj.eval(context), self._attr.eval(context))


class FormatString(LazyNodeBase):
    """A lazy object that represents a string template
    `template` together with a context `context` used
    to fill the template.

    The `template` is a lazy object that evaluates to
    a string. It will be evaluated when the `FormatString`
    is evaluated.

    The `context` must be a lazy object that evaluates to a
    dictionary that containd the keys 'args' and 'kwargs'.
    The values corresponding to these keys will be evaluated
    when the ``FormatString`` is evaluated and will be passed
    to the `format` method of the evaluated `template` as
    unpacked positional and keyword arguments,
    respectively."""

    _fields = ('template', 'context')

    def __init__(self, template, context):
        return LazyNodeBase.__init__(self, template, context)

    def eval(self, context=None):
        _fs = self._template.eval(context)
        _ctx = self._context.eval(context)
        return _fs.format(*_ctx.get('args', tuple()), **_ctx.get('kwargs', dict()))


class String(LazyNodeBase):
    """A lazy object that represents a string `s`.
    
    The passed object `s` should be a lazy object.
    It will be evaluated and passed through the built-in
    `str` method when the ``String`` is evaluated."""

    _fields = ('s',)

    def __init__(self, s):
        return LazyNodeBase.__init__(self, s)

    def eval(self, context=None):
        return str(self._s.eval(context))

    def format(self, *args, **kwargs):
        """Convert to a lazy :py:class:`~Palisade.FormatString` using the supplied arguments as a context."""
        return FormatString(
            template=self._s,
            context=dict(args=lazify(args),
                         kwargs=lazify(kwargs)))
