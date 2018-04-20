# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# lib/db tests
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## lib/db tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

# NOC modules
from noc.lib.db import *
from noc.lib.test import NOCTestCase


class DBTestCase(NOCTestCase):
    def test_check_pg_superuser(self):
        self.assertEquals(type(check_pg_superuser()), bool)

    def test_postgis(self):
        self.assertEquals(check_postgis(), True)

    def test_srs(self):
        self.assertEquals(check_srs(), True)
