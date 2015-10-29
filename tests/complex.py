#!/usr/bin/env python
# -*- coding:utf-8 -*-

import backquotes

spam = `'for i in "s" "p" "a" "m"; do printf $$i; done'`

print(`'printf $spam | tr [a-z] [A-Z]'`)
