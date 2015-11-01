#!/usr/bin/env python
# -*- coding:ascii -*-

import contextlib
import inspect
import linecache
import locale
import optparse
import os
import re
import string
import subprocess
import sys
import tempfile
import tokenize
import warnings


__all__ = ['shell', 'preprocess']
__version__ = '0.0.1'


_source_encoding_re = re.compile(r'coding[:=]\s*([-\w.]+)')


def shell(argstring):
    r"""Invoke shell commands substituted by variables in the current scope.
    """
    frame = inspect.currentframe().f_back
    variables = frame.f_globals.copy()
    variables.update(frame.f_locals)
    command = string.Template(argstring).substitute(variables)
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               shell=True)
    out, _err = process.communicate()
    return out.decode(locale.getpreferredencoding())


def preprocess(filename, readline):
    r"""Preprocess Python source code using backquotes into plain Python code.

    .. warning:: preprocess() blocks while processing entire source codes.
    """
    tokens = []
    inside_backquotes = False
    encoding = _detect_encoding(filename)
    quote_start = 0
    ENCODING = getattr(tokenize, 'ENCODING', None)
    for token in tokenize.generate_tokens(readline):
        type, string, (srow, scol), (erow, ecol), line = token
        if type is ENCODING:
            encoding = string
        elif string == '`':
            if inside_backquotes:
                # print(`ls`.splitlines())
                #          ^
                quote_end = scol
                quoted_string = line[quote_start:quote_end]
                if _is_quoted(quoted_string):
                    quoted_string = quoted_string[1:-1]
                tokens.extend([
                    (tokenize.STRING, _triple_quote(quoted_string)),
                    (tokenize.OP, ')'),
                ])
            else:
                # print(`ls`.splitlines())
                #       ^
                quote_start = ecol
                tokens.extend([
                    (tokenize.NAME, 'backquotes'),
                    (tokenize.OP, '.'),
                    (tokenize.NAME, 'shell'),
                    (tokenize.OP, '('),
                ])
            inside_backquotes ^= True
        else:
            if inside_backquotes:
                # print(`ls`.splitlines())
                #        ^^
                # quoted string will be extracted at the end of the quotation
                pass
            else:
                # print(`ls`.splitlines())
                # ^^^^^^    ^^^^^^^^^^^^^^
                tokens.append((type, string))
    return tokenize.untokenize(tokens)


@contextlib.contextmanager
def _append_to_python_path(path):
    current_python_path = os.getenv('PYTHONPATH', '')
    if current_python_path:
        os.environ['PYTHONPATH'] = ':'.join((current_python_path, path))
    else:
        os.environ['PYTHONPATH'] = path
    yield
    os.environ['PYTHONPATH'] = current_python_path


def _detect_encoding(filename):
    r"""Detect declared encoding of Python source code.

    If encoding is not declared, returns the system default encoding.
    """
    for lineno in (1, 2):
        line = linecache.getline(filename, lineno)
        try:
            return _source_encoding_re.search(line).group(1)
        except AttributeError:
            pass
    return sys.getdefaultencoding()


def _detect_environment(frame):
    r"""Detect how Python source code is executed.
    """
    if frame.f_code.co_filename == '<stdin>':
        if frame.f_locals.get('__file__') is None:
            return 'repr'
        else:
            return 'redirect'
    outer_frame = frame.f_back
    if outer_frame and outer_frame.f_locals.get('__name__') != '__main__':
        return 'module'
    else:
        return 'script'


def _exec(object, globals, locals):
    r"""A wrapper function to provide consistent interface among Python 2/3.
    """
    if sys.version_info < (3,):
        exec('exec object in globals, locals')
    else:
        exec(object, globals, locals)


def _is_quoted(s):
    r"""Returns whether if string is surrouded by quotations.
    """
    return s[0] in ('"', "'") and s[0] == s[-1]


def _triple_quote(s):
    r"""Returns raw triple single-quoted string.
    """
    return "r'''" + s + "'''"


def _main(argv=sys.argv[1:]):
    r"""Main entry point of this script.
    """
    usage = u'Usage: %prog -m backquotes [options] [FILE] [ARG, ...]'
    prog = os.path.basename(sys.executable)
    parser = optparse.OptionParser(usage=usage, version=__version__, prog=prog)
    parser.add_option(
        '-E',
        '--no-exec',
        dest='execute',
        action='store_false',
        default=True,
        help='stop after preprocessing stage and print preprocessed source')
    opts, args = parser.parse_args(argv)
    try:
        infile = open(args.pop(0), 'r')  # not 'rb'
    except IndexError:
        infile = sys.stdin
    with contextlib.closing(infile):
        preprocessed_source = preprocess(infile.name, infile.readline)
    if opts.execute:
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write(preprocessed_source)
            f.seek(0)
            with _append_to_python_path(os.path.dirname(infile.name)):
                return_code = subprocess.call([sys.executable, f.name] + args)
        sys.exit(return_code)
    else:
        sys.stdout.write(preprocessed_source)


if __name__ == '__main__':
    sys.exit(_main())
else:
    frame = inspect.currentframe().f_back
    while frame.f_code.co_filename.startswith('<frozen importlib'):
        frame = frame.f_back
    environment = _detect_environment(frame)
    if environment == ('redirect', 'repr'):
        warnings.warn(u"backquotes doesn't work on REPL.")
    elif environment == 'module':
        warnings.warn(
            u"backquotes doesn't work when imported by another script")
    elif sys.version_info < (3,):
        with open(frame.f_code.co_filename, 'rb') as f:
            source = preprocess(f.name, f.readline)
        _exec(source, frame.f_globals, frame.f_locals)
        sys.exit()
