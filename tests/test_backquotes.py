#!/usr/bin/env python
# -*- coding:utf-8 -*-

import distutils.version
import os
import tempfile
import textwrap
import unittest

import backquotes


class TestBackquotes(unittest.TestCase):
    def test___all__(self):
        self.assertEqual(backquotes.__all__, ['shell', 'preprocess'])

    def test___version__(self):
        version = distutils.version.StrictVersion(backquotes.__version__)
        self.assertTrue(version)

    def test_shell(self):
        spam = 'spam'
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
        """).encode('ascii')
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
