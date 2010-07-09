# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System Version Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.lib.app.simplereport import SimpleReport
from noc.lib.version import get_version
import os,sys,csv
import django
##
##
##
class ReportSystemVersion(SimpleReport):
    title="System Version"
    def get_data(self,**kwargs):
        versions=[
            ["NOC"    ,    get_version()],
            ["OS"     ,    " ".join(os.uname())],
            ["Python" ,    sys.version],
            ["PostgreSQL", self.execute("SELECT VERSION()")[0][0]],
        ]
        cv_path=os.path.join("contrib","lib","VERSION.csv")
        if os.path.exists(cv_path):
            with open(cv_path) as f:
                r=csv.reader(f)
                for row in r:
                    versions+=[row]
        return {
            "data" : versions
        }
