import numpy as np
import operator as op
import unittest2 as unittest

from rootpy import asrootpy
from rootpy.io import root_open, DoesNotExist
from rootpy.plotting import Hist1D, Hist2D, Profile1D, Efficiency, Graph
from rootpy.plotting.hist import _Hist, _Hist2D
from rootpy.plotting.profile import _ProfileBase

from DijetAnalysis.PostProcessing.Palisade import InputROOT


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

    def test_get_expr_histogram_binary_op(self):
        for _symbol, _op in [('+', op.add), ('*', op.mul)]:
            with self.subTest(operation=_symbol):
                _result_expr = self._ic.get_expr('"test:h1" {} "test:h2"'.format(_symbol))
                _result_direct = _op(self._ic.get_expr('"test:h1"'), self._ic.get_expr('"test:h2"'))
                # bin-by-bin comparison
                for _bin_1, _bin_2 in zip(_result_expr, _result_direct):
                    self.assertEqual(_bin_1.value, _bin_2.value)
                    self.assertEqual(_bin_1.error, _bin_2.error)


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

        self.assertEqual(_err.exception.args[0], 'triple')

