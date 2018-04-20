# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## reportobjectsummary Test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ReportApplicationTestCase

class reportobjectsummaryTestCase(ReportApplicationTestCase):
    posts=[
        {"report_type":"profile"},
        {"report_type":"domain"},
        {"report_type":"tag"},
        {"report_type":"domain-profile"},
    ]
