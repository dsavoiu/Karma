import numpy as np
import operator as op
import unittest2 as unittest

from rootpy import asrootpy
from rootpy.io import root_open, DoesNotExist
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency, Graph
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase

from Karma.PostProcessing.Palisade import InputROOT


class TestInputROOTClass(unittest.TestCase):
    def setUp(self):
        # back up functions
        self._backup_functions = InputROOT.functions
        InputROOT.functions = {}

    def tearDown(self):
        # restore backed up functions
        InputROOT.functions = self._backup_functions

    def test_add_function(self):
        @InputROOT.add_function
        def test_function(tobject): pass
        self.assertIn('test_function', InputROOT.functions)
        self.assertIs(InputROOT.get_function('test_function'), test_function)

    def test_add_function_alias(self):
        @InputROOT.add_function(name='aliased_function')
        def test_function(tobject): pass
        self.assertIn('aliased_function', InputROOT.functions)
        self.assertNotIn('test_function', InputROOT.functions)
        self.assertIs(InputROOT.get_function('aliased_function'), test_function)

    def test_add_function_twice_nooverride_raises(self):
        @InputROOT.add_function
        def test_function(tobject): pass
        with self.assertRaises(ValueError):
            @InputROOT.add_function
            def test_function(tobject): pass

    def test_add_function_override(self):
        @InputROOT.add_function(override=True)
        def test_function(tobject): pass
        self.assertIn('test_function', InputROOT.functions)

    def test_get_function(self):
        @InputROOT.add_function
        def test_function(tobject): pass
        self.assertIs(InputROOT.get_function('test_function'), test_function)

    def test_get_function_override(self):
        @InputROOT.add_function
        def test_function(tobject): pass

        @InputROOT.add_function(name='test_function', override=True)
        def test_function_2(tobject): pass

        self.assertIn('test_function', InputROOT.functions)
        self.assertNotIn('test_function_2', InputROOT.functions)
        self.assertIs(InputROOT.get_function('test_function'), test_function_2)


class TestInputROOTNoFile(unittest.TestCase):

    def setUp(self):
        self._ic = InputROOT()

    def test_request_objspec_raises(self):
        with self.assertRaises(ValueError):
            self._ic.request([dict(object_spec="file0:directory/object")])

    def test_request_filenick_objpath_raises(self):
        with self.assertRaises(ValueError):
            self._ic.request([dict(file_nickname='file0', object_path="directory/object")])

    def test_get_raises(self):
        with self.assertRaises(ValueError):
            self._ic.get(object_spec="file0:directory/object")

    def test_get_expr_raises(self):
        with self.assertRaises(ValueError):
            self._ic.get_expr('"file0:directory/object" + "file0:directory/object2"')

    def test_add_file(self):
        for nickname in (None, 'testfile'):
            with self.subTest():
                self._ic.add_file('ref/test.root', nickname=nickname)
                self.assertIn('ref/test.root', self._ic._file_nick_to_realpath)
                if nickname is not None:
                    self.assertIn('testfile', self._ic._file_nick_to_realpath)
                self.assertEqual(len(self._ic._input_controllers), 1)
                self.assertTrue(list(self._ic._input_controllers)[0].endswith('test.root'))


class TestInputROOTWithFile(unittest.TestCase):
    def setUp(self):

        self._ic = InputROOT()
        self._ic.add_file('ref/test.root', nickname='test')

    def test_get_inexistent_raises(self):
        with self.assertRaises(DoesNotExist):
            self._ic.get(object_spec="test:this_does_not_exist")

    def test_get_expr_inexistent_raises(self):
        with self.assertRaises(DoesNotExist):
            self._ic.get_expr('"test:this_does_not_exist"')

    def test_get(self):
        self.assertIsInstance(self._ic.get(object_spec="test:h1"), _Hist)
        self.assertIsInstance(self._ic.get(object_spec="test:h2"), _Hist)

    def test_get_expr_simple(self):
        self.assertIsInstance(self._ic.get_expr('"test:h1"'), _Hist)
        self.assertIsInstance(self._ic.get_expr('"test:h2"'), _Hist)

    def test_get_expr_simple_string(self):
        self.assertEquals(self._ic.get_expr('str("test:h1")'), "test:h1")

    def test_get_expr_histogram_binary_op(self):
        for _symbol, _op in [('+', op.add), ('*', op.mul)]:
            with self.subTest(operation=_symbol):
                _result_expr = self._ic.get_expr('"test:h1" {} "test:h2"'.format(_symbol))
                _result_direct = _op(self._ic.get_expr('"test:h1"'), self._ic.get_expr('"test:h2"'))
                # bin-by-bin comparison
                for _bin_1, _bin_2 in zip(_result_expr, _result_direct):
                    self.assertEqual(_bin_1.value, _bin_2.value)
                    self.assertEqual(_bin_1.error, _bin_2.error)

    def test_get_expr_binary_op_noinput(self):
        self.assertEquals(self._ic.get_expr('no_input("test:h1"+"_"+"test:h2")'), "test:h1_test:h2")

    def test_get_expr_user_defined_function(self):

        # add a custom function: scale hist by a factor 3
        @InputROOT.add_function
        def triple(tobject):
            return 3 * tobject

        # evaluate expr and compute reference reult
        _result_expr = self._ic.get_expr('triple("test:h1")')
        _result_direct = 3 * self._ic.get_expr('"test:h1"')

        # bin-by-bin comparison
        for _bin_1, _bin_2 in zip(_result_expr, _result_direct):
            self.assertEqual(_bin_1.value, _bin_2.value)
            self.assertEqual(_bin_1.error, _bin_2.error)

        # remove function to avoid side effects
        InputROOT.functions.pop('triple', None)

    def test_get_expr_undefined_user_defined_function_raise(self):

        with self.assertRaises(KeyError) as _err:
            # evaluate expr and compute reference reult
            self._ic.get_expr('triple("test:h1")')

        self.assertIn("'triple'", _err.exception.args[0])

    def test_get_expr_user_defined_function_signatures(self):

        @InputROOT.add_function
        def divide(dividend, divisor=8):
            return dividend / divisor

        # subtests for correct application of signatures
        with self.subTest(test_label="kwarg_default"):
            self.assertEqual(self._ic.get_expr('divide(16)'), 2)
        with self.subTest(test_label="kwarg_explicit_as_positional"):
            self.assertEqual(self._ic.get_expr('divide(16, 2)'), 8)
        with self.subTest(test_label="kwarg_explicit"):
            self.assertEqual(self._ic.get_expr('divide(16, divisor=4)'), 4)
        with self.subTest(test_label="kwarg_and_positional_explicit"):
            self.assertEqual(self._ic.get_expr('divide(dividend=42, divisor=7)'), 6)
        with self.subTest(test_label="kwarg_and_positional_explicit_different_order"):
            self.assertEqual(self._ic.get_expr('divide(divisor=5, dividend=35)'), 7)

        # subtests for exceptions
        with self.subTest(test_label="too_few_args"):
            with self.assertRaises(TypeError) as _err:
                self._ic.get_expr('divide()')
        with self.subTest(test_label="too_many_args"):
            with self.assertRaises(TypeError) as _err:
                self._ic.get_expr('divide(1,2,3)')
        with self.subTest(test_label="multiple_values_for_kwarg"):
            with self.assertRaises(TypeError) as _err:
                self._ic.get_expr('divide(1,2,divisor=3)')
        with self.subTest(test_label="wrong_kwarg"):
            with self.assertRaises(TypeError) as _err:
                self._ic.get_expr('divide(42, bogus_kwarg=30)')

        # remove function to avoid side effects
        InputROOT.functions.pop('divide', None)

    def test_get_expr_user_defined_function_argtypes(self):

        @InputROOT.add_function
        def get_type(argument):
            return type(argument)

        # subtests for correct application of signatures
        with self.subTest(test_label="int"):
            self.assertTrue(self._ic.get_expr('get_type(16)') is int)
        with self.subTest(test_label="float"):
            self.assertTrue(self._ic.get_expr('get_type(13.4)') is float)
        with self.subTest(test_label="bool"):
            self.assertTrue(self._ic.get_expr('get_type(True)') is bool)
            self.assertTrue(self._ic.get_expr('get_type(False)') is bool)
        with self.subTest(test_label="none"):
            self.assertTrue(self._ic.get_expr('get_type(None)') is type(None))

        with self.subTest(test_label="unknown_identifier_raise"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('get_type(bogus_identifier)')

        # remove function to avoid side effects
        InputROOT.functions.pop('get_type', None)


    def test_get_expr_user_defined_function_varargs(self):

        @InputROOT.add_function
        def get_arg_structure(*args, **kwargs):
            return dict(args=args, kwargs=kwargs)

        # subtests for correct application of signatures
        with self.subTest(test_label="no_args"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure()'),
                dict(args=tuple(), kwargs={})
            )
        with self.subTest(test_label="positional_args_only"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure(1, 6, 4)'),
                dict(args=(1, 6, 4), kwargs={})
            )
        with self.subTest(test_label="kwargs_only"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure(key1=3, key2=77)'),
                dict(args=tuple(), kwargs=dict(key1=3, key2=77))
            )
        with self.subTest(test_label="positional_and_kwargs"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure(2, 44, key=92)'),
                dict(args=(2, 44), kwargs=dict(key=92))
            )

        with self.subTest(test_label="starred_args_in_expression"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure(*[3, 2])'),
                dict(args=(3, 2), kwargs=dict())
            )

        with self.subTest(test_label="args_and_starred_args_in_expression"):
            self.assertEquals(
                self._ic.get_expr('get_arg_structure(1, *[2, 3])'),
                dict(args=(1, 2, 3), kwargs={})
            )

        with self.subTest(test_label="starred_kwargs_in_expression"):
            with self.assertRaises(NotImplementedError) as _err:
                self._ic.get_expr('get_arg_structure(**{"a": 3})')

        # remove function to avoid side effects
        InputROOT.functions.pop('get_arg_structure', None)

    def test_get_expr_local_variables(self):

        with self.subTest(test_label="call_local_variable"):
            self.assertEqual(self._ic.get_expr('my_local', locals={'my_local': 60}), 60)

        with self.subTest(test_label="call_local_variable_list"):
            self.assertEqual(self._ic.get_expr('my_local', locals={'my_local': [42, 60, 93]}), [42, 60, 93])
            self.assertEqual(self._ic.get_expr('my_local[2]', locals={'my_local': [42, 60, 93]}), 93)
            with self.assertRaises(IndexError) as _err:
                self._ic.get_expr('my_local[44]', locals={'my_local': [42, 60, 93]})

        with self.subTest(test_label="registered_local_variable_before_creation_raise"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('my_local')

        self._ic.register_local('my_local', 42)

        with self.subTest(test_label="registered_local_variable_value"):
            self.assertEqual(self._ic.get_expr('my_local'), 42)

        with self.subTest(test_label="registered_local_variable_value_overridden_in_call"):
            self.assertEqual(self._ic.get_expr('my_local', {'my_local': 93}), 93)

        with self.subTest(test_label="disallow_local_variables_raise"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('my_local', locals=None)

        with self.subTest(test_label="inexistent_local_variable_raise"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('my_bogus_local')

        self._ic.clear_locals()

        with self.subTest(test_label="local_variable_after_deletion_raise"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('my_local')

    def test_get_expr_local_variables_self_referential(self):

        self._ic.register_local('selfref_direct', 'selfref_direct')
        self._ic.register_local('selfref_list_direct', ['selfref_list_direct[0]', 'selfref_list_direct[1]'])
        self._ic.register_local('selfref_list_cross', ['selfref_list_cross[1]', 'selfref_list_cross[0]'])
        self._ic.register_local('selfref_resolvable', ['selfref_resolvable[1]', 42])

        with self.subTest(test_label="selfref_direct"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('selfref_direct')

        with self.subTest(test_label="selfref_list_direct"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('selfref_list_direct[0]')
                self._ic.get_expr('selfref_list_direct[1]')
        with self.subTest(test_label="selfref_list_cross"):
            with self.assertRaises(NameError) as _err:
                self._ic.get_expr('selfref_list_cross[0]')
                self._ic.get_expr('selfref_list_cross[1]')

        # this won't work in the current implementation, but is an extreme edge case anyway:
        #with self.subTest(test_label="selfref_resolvable"):
        #    self.assertEquals(self._ic.get_expr('selfref_resolvable[0]'), 42)
        #    self.assertEquals(self._ic.get_expr('selfref_resolvable[1]'), 42)
