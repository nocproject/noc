# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
import os,sys
import django

class Report(noc.main.report.Report):
    name="main.system"
    title="System version"
    requires_cursor=False
    columns=[Column("Component"),Column("Version")]
    def get_queryset(self):
        return [
            ["OS"," ".join(os.uname())],
            ["Python",sys.version],
            ["Django","%d.%d %s"%django.VERSION],
            # NOC Version, hg tip
        ]
