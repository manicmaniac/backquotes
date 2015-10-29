#!/usr/bin/env python
# -*- coding:utf-8 -*-

from distutils.core import setup

from backquotes import __version__ as version


def read(path):
    with open(path) as f:
        return f.read()


setup(
    name='backquotes',
    version=version,
    description='shell command invocation with backquotes, like Perl, Ruby.',
    long_description=read('README.rst'),
    keywords='backquote shell syntax perl ruby sh bash',
    author='Ryosuke Ito',
    author_email='rito.0305@gmail.com',
    url='https://github.com/manicmaniac/backquotes',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    py_modules=['backquotes'],
)
