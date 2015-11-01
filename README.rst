backquotes
==========

.. image:: https://travis-ci.org/manicmaniac/backquotes.svg?branch=master
    :target: https://travis-ci.org/manicmaniac/backquotes

Introduction
------------

``backquotes`` brings (Perl / Ruby)'s shell invocation syntax to Python.

``backquotes`` is experimental module by now,
using it in a serious program is not recommended.

Syntax
------

Firstly, remember to import ``backquotes`` module.

.. code:: python

    import backquotes

Basic
-----

You can use similar syntax to Perl / Ruby.

.. code:: python

    import backquotes
    print(`date`)

Pipes and redirections
----------------------

Yes, you can use pipes, redirections too.

.. code:: python

    import backquotes
    print(`ls | tr [a-z] [A-Z]`.splitlines())

Local variables substitution
----------------------------

To bring local variables in Python code to shell command,
use Perl-like variables substitution.

.. code:: python

    import backquotes
    spam = 'spam'
    print(`echo $spam`)

``$$`` is substituted to a literal ``$``.

.. code:: python

    import backquotes
    print(`echo $$PATH`)

Usage
-----

Runtime-preprocessing
^^^^^^^^^^^^^^^^^^^^^

You can use runtime-preprocessing only in Python 2.
This works transparently when you import ``backquotes``.

.. warning::

    Python 3 raises `SyntaxError` on a backquote character before evaluate the first line.
    So you CANNOT use runtime-preprocessing.

.. code:: python

    #!/usr/bin/env python
    import backquotes
    print(`date`)

Save as ``date.py``, and run it as usual.

.. code:: sh

    python date.py

You will see the result of ``date`` command.

Runtime-preprocessing sometimes causes ``SyntaxError`` before preprocessing starts,
especially with complex commands invocation.
You can avoid this error by using single-quotes just inside the backquotes.

.. code:: python

    print(`'for file in *; do echo $file; done'`)

Execute `backquotes` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ``python`` with ``-m backquotes`` option to invoke ``backquotes`` as a script.
``backquotes`` compiles a plain Python code and execute it.

.. note::

    This works both in Python 2 / 3.

.. code:: sh

    python -m backquotes date.py

You can pass arguments to the script.

.. code:: sh

    python -m backquotes date.py 2015 10 31

Preprocess Python code
^^^^^^^^^^^^^^^^^^^^^^

Run ``python`` with ``-m backquotes -E`` option to only preprocess the given source file
and print to stdout.

.. warning::

    Preprocessed python code is almost the same as the original code semantically,
    but whitespaces are moved by the preprocessor.

.. note::

    This works both in Python 2 / 3.

.. code:: sh

    mkdir dist
    python -m backquotes -E date.py > dist/date.py
    python dist/date.py


Restrictions
------------

- ``backquotes`` does not work in Python REPL.  Import it in REPL causes warnings.
- a module which imports ``backquotes`` does not work when it is imported.

Install
-------

.. code:: sh

    pip install backquotes

or

.. code:: sh

    git clone https://github.com/manicmaniac/backquotes.git
    cd backquotes
    python setup.py install

or

.. code:: sh

    wget https://raw.githubusercontent.com/manicmaniac/backquotes/master/backquotes.py
