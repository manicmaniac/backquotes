#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

import backquotes

os.environ['SPAM'] = 'SPAM'
print(`'printf $$SPAM'`)
