# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# lib/sysutils tests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## lib/sysutils tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# NOC modules
from noc.lib.test import NOCTestCase
from noc.lib.sysutils import *


class SysutilsTestCase(NOCTestCase):
    def test_get_cpu_cores(self):
        nc = get_cpu_cores()
        self.assertTrue(type(nc) == int or type(nc) == long)
        self.assertTrue(nc >= 1)
