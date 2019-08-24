import itertools
import numpy as np
import operator as op
import unittest2 as unittest

from Karma.PostProcessing.Palisade import (
    ContextValue, InputValue,
    Lazy, String, lazify, If, Try
)


class TestLazyNodes(unittest.TestCase):
    def setUp(self):
        self._values = (2, 'f', lambda: None, [7], dict(a='b'))

    def test_lazy_hash(self):
        # ensure hashes are identical
        self.assertEquals(
            hash(Lazy((2, 'f', lambda: None))),
            hash(Lazy((2, 'f', lambda: None))),
        )

    def test_lazy_eval_roundtrip(self):
        for _value in self._values:
            with self.subTest(value=_value):
                self.assertEquals(Lazy(_value).eval(), _value)

    def test_double_lazy_eval_roundtrip(self):
        for _value in self._values:
            with self.subTest(value=_value):
                self.assertEquals(Lazy(Lazy(_value)).eval().eval(), _value)

    def test_lazify_eval_roundtrip(self):
        for _value in self._values:
            with self.subTest(value=_value):
                self.assertEquals(lazify(_value).eval(), _value)

    def test_lazy_list_iterable(self):
        l = [1, 4, 6, 6]
        for el, lazy_el in zip(l, lazify(l)):
            self.assertEquals(el, lazy_el.eval())

    def test_lazy_string_cast(self):
        self.assertEquals(String(2).eval(), str(2))

    def test_lazy_string_format(self):
        self.assertEquals(String("{0}{0}").format('a').eval(), 'aa')
        self.assertEquals(String("{0}{1}").format('a', 'b').eval(), 'ab')
        self.assertEquals(String("{}{}").format('a', 'b').eval(), 'ab')
        self.assertEquals(String("{a}{b}").format(a='a', b='b').eval(), 'ab')
        self.assertEquals(String("{a}{b}").format(b='a', a='b').eval(), 'ba')
        self.assertEquals(String("{0}{b}").format('a', b='b').eval(), 'ab')
        self.assertEquals(String("{}{b}").format('a', b='b').eval(), 'ab')

    def test_lazy_unary(self):
        _vals = (14, 28)
        _eager = lambda x: x
        for _val in _vals:
            self.assertEquals((-Lazy(_val)).eval(), -_val)
            self.assertEquals((+Lazy(_val)).eval(), +_val)
            self.assertEquals((~Lazy(_val)).eval(), ~_val)

    def test_lazy_arithmetic(self):
        _vals = (14, 28)
        _eager = lambda x: x
        for _a, _b in itertools.product(_vals, _vals):
            for _config in [(Lazy, Lazy), (Lazy, _eager), (_eager, Lazy)]:
                # simple binary expressions
                self.assertEquals((_config[0](_a) + _config[1](_b)).eval(), _a + _b)
                self.assertEquals((_config[0](_a) - _config[1](_b)).eval(), _a - _b)
                self.assertEquals((_config[0](_a) * _config[1](_b)).eval(), _a * _b)
                self.assertEquals((_config[0](_a) / _config[1](_b)).eval(), _a / _b)

        # complex expression
        self.assertEquals((3 * (Lazy(14) - 22)).eval(), -24)

    def test_lazy_comparisons(self):
        _vals = (14, 28)
        _eager = lambda x: x
        for _a, _b in itertools.product(_vals, _vals):
            for _config in [(Lazy, Lazy), (Lazy, _eager), (_eager, Lazy)]:
                # simple binary expressions
                self.assertEquals((_config[0](_a) != _config[1](_b)).eval(), _a != _b)
                self.assertEquals((_config[0](_a) == _config[1](_b)).eval(), _a == _b)
                self.assertEquals((_config[0](_a) <  _config[1](_b)).eval(), _a <  _b)
                self.assertEquals((_config[0](_a) <= _config[1](_b)).eval(), _a <= _b)
                self.assertEquals((_config[0](_a) >  _config[1](_b)).eval(), _a >  _b)
                self.assertEquals((_config[0](_a) >= _config[1](_b)).eval(), _a >= _b)

    def test_lazy_logic(self):
        _vals = (True, False)
        _eager = lambda x: x
        for _a, _b in itertools.product(_vals, _vals):
            for _config in [(Lazy, Lazy), (Lazy, _eager), (_eager, Lazy)]:
                # simple binary expressions
                self.assertEquals((_config[0](_a) & _config[1](_b)).eval(), _a & _b)
                self.assertEquals((_config[0](_a) | _config[1](_b)).eval(), _a | _b)
                self.assertEquals((_config[0](_a) ^ _config[1](_b)).eval(), _a ^ _b)

    def test_lazy_callable(self):
        _vals = (14, 28, "a")

        doubler_lambda = lambda x: 2 * x

        def doubler_func(x):
            return 2 * x

        class doubler_class:
            def __call__(self, x):
                return 2 * x

        for _callable in (doubler_lambda, doubler_func, doubler_class()):
            for _val in _vals:
                # simple binary expressions
                self.assertEquals((Lazy(_callable)(_val)).eval(), _callable(_val))

    def test_lazy_attribute(self):
        class class_with_attributes:
            def __init__(self):
                self.attr = 'value'

        _instance = class_with_attributes()

        self.assertEquals(Lazy(_instance).attr.eval(), _instance.attr)

        _lazy_inexistent_attr = Lazy(_instance).inexistent_attr
        with self.assertRaises(AttributeError):
            _lazy_inexistent_attr.eval()

    def test_lazy_conditional(self):
        _vals = (True, False)
        for _val in _vals:
            # simple binary expressions
            self.assertEquals((
                If(Lazy(_val), 'truey', 'falsy')
            ).eval(), 'truey' if _val else 'falsy')

    def test_lazy_exception_handling(self):
        # TypeError raised -> catch
        self.assertEquals(
            Try(Lazy(len)(2), TypeError, 'ERROR').eval(),
            'ERROR'
        )
        # TypeError is Exception subclass -> catch
        self.assertEquals(
            Try(Lazy(len)(2), Exception, 'ERROR').eval(),
            'ERROR'
        )
        # TypeError is not OSError -> raise
        with self.assertRaises(TypeError):
            Try(Lazy(len)(2), OSError, 'ERROR').eval()


class TrivialInputController(object):
    def get_expr(self, expression):
        return '<'+str(expression)+'>'


class TestContextInputValues(unittest.TestCase):
    def setUp(self):
        self._ic = TrivialInputController()
        self._context = {
            'namespace' : {
                'key_1' : 'value_1',
                'key_2' : 'value_2',
                'meta_key' : 'key_1',
            },
            '_input_controller' : self._ic,
        }
        self._values = (2, 'f', lambda: None, [7], dict(a='b'))

    def test_context_value_simple(self):
        _cval = ContextValue('namespace[key_1]')
        self.assertEquals(_cval.eval(self._context), self._context['namespace']['key_1'])

    def test_context_value_expression(self):
        _cval = ContextValue('namespace[key_1]') + ContextValue('namespace[key_2]')
        self.assertEquals(_cval.eval(self._context), self._context['namespace']['key_1'] + self._context['namespace']['key_2'])

    def test_context_value_nested(self):
        _cval = ContextValue(String("namespace[{}]").format(ContextValue('namespace[meta_key]')))
        self.assertEquals(_cval.eval(self._context), self._context['namespace']['key_1'])

    def test_input_value_simple(self):
        _expr = 'a34fc'
        _ival = InputValue(_expr)
        self.assertEquals(
            _ival.eval(self._context),
             self._ic.get_expr(_expr)
        )

    def test_input_value_expression(self):
        _expr_1, _expr_2 = 'a34fc', '234rddd'
        _ival = InputValue(_expr_1) + InputValue(_expr_2)
        self.assertEquals(
            _ival.eval(self._context),
             self._ic.get_expr(_expr_1) + self._ic.get_expr(_expr_2)
        )
