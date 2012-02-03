# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/sysutils tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from noc.lib.test import NOCTestCase
from noc.lib.sysutils import *


class SysutilsTestCase(NOCTestCase):
    def test_get_cpu_cores(self):
        nc = get_cpu_cores()
        self.assertTrue(type(nc) == int or type(nc) == long)
        self.assertTrue(nc >= 1)
