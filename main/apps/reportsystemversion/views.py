# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System Version Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport
from noc.lib.version import get_version
import os,sys
import django
##
##
##
class ReportSystemVersion(SimpleReport):
    title="System Version"
    def get_data(self,**kwargs):
        return {
            "data" : [
                ["NOC"    ,    get_version()],
                ["OS"     ,    " ".join(os.uname())],
                ["Python" ,    sys.version],
                ["Django" ,    "%s"%str(django.VERSION)],
                ["PostgreSQL", self.execute("SELECT VERSION()")[0][0]],
            ]
        }
