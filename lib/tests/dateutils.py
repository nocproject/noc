# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/dateutils tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.test import NOCTestCase
from noc.lib.dateutils import *


class DateutilsTestCase(NOCTestCase):
    def test_total_seconds(self):
        # 1s
        self.assertEquals(total_seconds(datetime.timedelta(seconds=1)), 1.0)
        # 1m
        self.assertEquals(total_seconds(datetime.timedelta(minutes=1)), 60.0)
        # 1h
        self.assertEquals(total_seconds(datetime.timedelta(hours=1)), 3600.0)
        # 1day
        self.assertEquals(total_seconds(datetime.timedelta(days=1)), 86400.0)
        # 7days
        self.assertEquals(total_seconds(datetime.timedelta(days=7)), 604800.0)
        # 1mks
        self.assertEquals(total_seconds(datetime.timedelta(microseconds=1)),
                          1e-6)
        # 1day 1h 1m 1s 1msk
        self.assertEquals(total_seconds(
            datetime.timedelta(days=1, hours=1, minutes=1, microseconds=1)),
            90060.000001
        )


