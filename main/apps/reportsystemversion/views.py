# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## System Version Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.lib.app.simplereport import *
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
            SectionRow("Host Software"),
            ["OS"     ,    " ".join(os.uname())],
            ["Python" ,    sys.version],
            ["PostgreSQL", self.execute("SELECT VERSION()")[0][0]],
            SectionRow("Contributed Software (contrib/)"),
        ]
        cv_path=os.path.join("contrib","lib","VERSION.csv")
        if os.path.exists(cv_path):
            with open(cv_path) as f:
                r=csv.reader(f)
                for row in r:
                    versions+=[row]
        versions+=[SectionRow("Python Path")]
        for p in sys.path:
            versions+=[("",p)]
        return self.from_dataset(title=self.title,columns=["Component","Version"],data=versions)
