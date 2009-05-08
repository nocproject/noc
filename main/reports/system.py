# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
from noc.lib.version import get_version
import os,sys
import django

class Report(noc.main.report.Report):
    name="main.system"
    title="System version"
    requires_cursor=True
    columns=[Column("Component"),Column("Version")]
    def get_queryset(self):
        return [
            ["NOC"    , get_version()],
            ["OS"     , " ".join(os.uname())],
            ["Python" , sys.version],
            ["Django" , "%s"%str(django.VERSION)],
            ["PostgreSQL", self.execute("SELECT VERSION()")[0][0]],
        ]
