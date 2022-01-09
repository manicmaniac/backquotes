# -*- coding:utf-8 -*-

import distutils.version
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
try:
    from test.test_support import EnvironmentVarGuard, captured_stdout
except ImportError:
    from test.support import EnvironmentVarGuard, captured_stdout
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
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

    def test__append_to_python_path_when_python_path_is_not_set(self):
        with EnvironmentVarGuard() as env:
            del env['PYTHONPATH']
            with backquotes._append_to_python_path('spam'):
                self.assertEqual(env['PYTHONPATH'], 'spam')

    def test__append_to_python_path_when_python_path_is_set(self):
        with EnvironmentVarGuard() as env:
            env['PYTHONPATH'] = 'spam'
            with backquotes._append_to_python_path('ham'):
                self.assertEqual(env['PYTHONPATH'], 'spam:ham')

    def test__detect_environment_when_filename_is_stdin_and_file_does_not_exist(self):
        frame = MagicMock()
        frame.f_code.co_filename = '<stdin>'
        frame.f_locals.get.return_value = None
        self.assertEqual(backquotes._detect_environment(frame), 'repl')

    def test__detect_environment_with_filename_is_stdin_and_file_exists(self):
        frame = MagicMock()
        frame.f_code.co_filename = '<stdin>'
        frame.f_locals = {'__file__': 'spam'}
        self.assertEqual(backquotes._detect_environment(frame), 'redirect')

    def test__detect_environment_with_filename_is_not_stdin_and_name_is_not_main(self):
        frame = MagicMock()
        frame.f_code.co_filename = 'spam'
        frame.f_back.f_locals = {'__name__': 'ham'}
        self.assertEqual(backquotes._detect_environment(frame), 'module')

    def test__detect_environment_with_filename_is_not_stdin_and_name_is_main(self):
        frame = MagicMock()
        frame.f_code.co_filename = 'spam'
        frame.f_back.f_locals = {'__name__': '__main__'}
        self.assertEqual(backquotes._detect_environment(frame), 'script')

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

    def test_import_in_repl(self):
        with tempfile.TemporaryFile('w+') as f:
            f.write('import backquotes\n')
            f.seek(0)
            process = subprocess.Popen([sys.executable],
                                       stdin=f,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        out, err = process.communicate()
        self.assertEqual(out, b'')
        self.assertIn(b'UserWarning:', err)

    def assertIn(self, member, container, msg=None):
        try:
            super(TestBackquotes, self).assertIn(member, container, msg)
        except AttributeError:
            self.assertTrue(member in container, msg)
