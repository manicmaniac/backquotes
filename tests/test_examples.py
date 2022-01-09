#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import contextlib
import imp
import os
import subprocess
import sys
import tempfile
try:
    from test.support import check_warnings
except ImportError:
    from test.test_support import check_warnings
import unittest


old_python_path = os.getenv('PYTHONPATH', '')
new_python_path = os.path.dirname(os.path.dirname(__file__))
os.environ['PYTHONPATH'] = ':'.join((old_python_path, new_python_path))

import backquotes


class ExampleTestCase(unittest.TestCase):
    def test_run(self):
        if self.__class__ is not ExampleTestCase:
            if sys.version_info < (3,):
                args = [sys.executable, self.fixture]
                self.assert_subprocess_outputs(args)

    def test_compile_and_run(self):
        if self.__class__ is not ExampleTestCase:
            args = [sys.executable, backquotes.__file__, self.fixture]
            self.assert_subprocess_outputs(args)

    def test_preprocess_and_run(self):
        if self.__class__ is not ExampleTestCase:
            with tempfile.NamedTemporaryFile() as f:
                args = [sys.executable, backquotes.__file__, '-E', self.fixture]
                process = subprocess.Popen(args, stdout=f)
                process.communicate()
                f.seek(0)
                self.assertEqual(process.returncode, 0)
                args = [sys.executable, f.name]
                self.assert_subprocess_outputs(args)

    def assert_subprocess_outputs(self, args):
        PIPE = subprocess.PIPE
        process = subprocess.Popen(args, stdout=PIPE)
        result = process.communicate()
        self.assertEqual(result[0], self.expected)
        self.assertEqual(process.returncode, 0)

    @property
    def name(self):
        if self.__class__ is not ExampleTestCase:
            return self.__class__.__name__[4:].lower()

    @property
    def fixture(self):
        if self.__class__ is not ExampleTestCase:
            file, pathname, description = imp.find_module(self.name, [os.path.dirname(__file__)])
            with contextlib.closing(file):
                return pathname


class TestComplex(ExampleTestCase):
    expected = b'SPAM\n'


class TestEscape(ExampleTestCase):
    expected = b'SPAM\n'


class TestHello(ExampleTestCase):
    expected = b'hello\n'


class TestPipe(ExampleTestCase):
    expected = b'SPAM\n'


class TestUnicode(ExampleTestCase):
    expected = b'\xe3\x82\xb9\xe3\x83\x91\xe3\x83\xa0\n'

class TestVariables(ExampleTestCase):
    expected = b'SPAM\n'


if __name__ == '__main__':
    unittest.main()
