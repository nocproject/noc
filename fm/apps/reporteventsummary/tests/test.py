# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## reporteventsummary Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ReportApplicationTestCase

class reporteventsummaryTestCase(ReportApplicationTestCase):
    posts=[
        {"report_type":"class"},
        {"report_type":"priority"},
        {"report_type":"object"},
        {"report_type":"profile"}
    ]
