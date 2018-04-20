# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## reportlatestchanges Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ReportApplicationTestCase

class reportlatestchangesTestCase(ReportApplicationTestCase):
    posts=[
        {"repo":"config","days":"7"},
        {"repo":"dns","days":"7"},
        {"repo":"prefix-list","days":"7"},
    ]
