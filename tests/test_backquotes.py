#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import with_statement

import distutils.version
import os
import tempfile
import textwrap
import unittest
try:
    from test.test_support import captured_stdout
except ImportError:
    from test.support import captured_stdout
import backquotes


class TestBackquotes(unittest.TestCase):
    def test___all__(self):
        self.assertEqual(backquotes.__all__, ['shell', 'preprocess'])

    def test___version__(self):
        version = distutils.version.StrictVersion(backquotes.__version__)
        self.assertTrue(version)

    def test_shell(self):
        spam = 'spam'  # noqa
        result = backquotes.shell('printf $spam | tr [a-z] [A-Z]')
        self.assertEqual(result, 'SPAM')

    def test_preprocess(self):
        source = textwrap.dedent('''
        spam = 'spam'
        print(`printf $spam | tr [a-z] [A-Z]`)
        ''')
        expected = textwrap.dedent("""
        spam ='spam'
        print (backquotes .shell (r'''printf $spam | tr [a-z] [A-Z]'''))
        """)
        with tempfile.NamedTemporaryFile('w+') as f:
            f.write(source)
            f.seek(0)
            result = backquotes.preprocess(f.name, f.readline)
        self.assertEqual(result, expected)

    def test__append_to_python_path(self):
        def predicate():
            return os.getenv('PYTHONPATH').endswith('spam')
        with backquotes._append_to_python_path('spam'):
            self.assertTrue(predicate())
        self.assertFalse(predicate())

    def test__exec(self):
        backquotes._exec('self.test__exec_result = True', globals(), locals())
        self.assertTrue(self.test__exec_result)
        del self.test__exec_result

    def test__is_quoted(self):
        self.assertTrue(backquotes._is_quoted('"spam"'))
        self.assertFalse(backquotes._is_quoted('spam'))
        self.assertFalse(backquotes._is_quoted('"spam\''))

    def test__triple_quote(self):
        result = backquotes._triple_quote('spam')
        expected = "r'''spam'''"
        self.assertEqual(result, expected)

    def test__main_help(self):
        with captured_stdout() as s:
            self.assertRaises(SystemExit, backquotes._main, ['-h'])
            self.assertIn('Usage:', s.getvalue())
            self.assertRaises(SystemExit, backquotes._main, ['--help'])
            self.assertIn('Usage:', s.getvalue())

    def test__main_version(self):
        with captured_stdout() as s:
            self.assertRaises(SystemExit, backquotes._main, ['--version'])
            self.assertEqual(backquotes.__version__ + '\n', s.getvalue())

    def assertIn(self, member, container, msg=None):
        try:
            super(TestBackquotes, self).assertIn(member, container, msg)
        except AttributeError:
            self.assertTrue(member in container, msg)
