# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Module Import test case
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils import unittest  # unittest2 backport


class ImportTestCase(unittest.TestCase):
    """
    Test there are no import errors with module
    """
    def __init__(self, module):
        super(ImportTestCase, self).__init__()
        self.module = module

    def __str__(self):
        return "<ImportTestCase: '%s'>" % self.module

    def runTest(self):
        __import__(self.module, {}, {}, "*")
