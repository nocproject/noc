# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/version tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
# NOC modules
from noc.lib.ip import *
from noc.lib.version import *
from noc.lib.test import NOCTestCase


class VersionTestCase(NOCTestCase):
    """
    Test version functions
    """
    def test_split(self):
        v = split_version("0.7")
        self.assertEquals(v, (0, 7, None, None, None))
        v = split_version("0.7.0")
        self.assertEquals(v, (0, 7, None, None, None))
        v = split_version("0.7.1")
        self.assertEquals(v, (0, 7, 1, None, None))
        v = split_version("0.7(5)")
        self.assertEquals(v, (0, 7, None, 5, None))
        v = split_version("0.7.1(5)")
        self.assertEquals(v, (0, 7, 1, 5, None))
        v = split_version("0.7(5)r4995")
        self.assertEquals(v, (0, 7, None, 5, 4995))
        v = split_version("0.7.1(5)r4995")
        self.assertEquals(v, (0, 7, 1, 5, 4995))
        with self.assertRaises(ValueError):
            v = split_version("X.Y.Z")

    def test_cmp(self):
        v = cmp_version("0.7", "0.7")
        self.assertEquals(v == 0, True)
        v = cmp_version("0.7", "0.7.0")
        self.assertEquals(v == 0, True)
        v = cmp_version("0.7", "0.7.1")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.1", "0.7")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.1", "0.7.1")
        self.assertEquals(v == 0, True)
        v = cmp_version("0.7.1", "0.7.2")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.2", "0.7.1")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.2", "0.7.11")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.1", "0.7.1(1)")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.1(1)", "0.7.1")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.1(1)", "0.7(1)")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.1(1)", "0.7.1(1)")
        self.assertEquals(v == 0, True)
        v = cmp_version("0.7.1(1)", "0.7.1(2)")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.1(2)", "0.7.1(1)")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.1(2)", "0.7.1(11)")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7.1(2)", "0.7.1(2)r1234")
        self.assertEquals(v > 0, True)
        v = cmp_version("0.7.1(2)r1234", "0.7.1(2)")
        self.assertEquals(v < 0, True)
        v = cmp_version("0.7", "0.7.1(2)r1245")
        self.assertEquals(v < 0, True)
