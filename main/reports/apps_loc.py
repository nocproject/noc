# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
import os

class Report(noc.main.report.Report):
    name="main.apps_loc"
    title="Lines of code"
    requires_cursor=False
    columns=[Column("App"),
            Column(".py lines",align="RIGHT",summary="sum"),
            Column(".html lines",align="RIGHT",summary="sum"),
            Column(".rst lines",align="RIGHT",summary="sum"),
            Column(".mib lines",align="RIGHT",summary="sum"),
            Column("Other lines",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        def loc(f):
            f=open(f)
            d=f.read()
            f.close()
            return len(d.split("\n"))
        r=[]
        for dirname in [d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")]:
            if dirname in ["contrib","dist","build"]:
                continue
            py_loc=0
            html_loc=0
            rst_loc=0
            mib_loc=0
            other_loc=0
            for dirpath,dirnames,filenames in os.walk(dirname):
                for f in [f for f in filenames if not (f.endswith(".pyc") or f.endswith(".pyo"))]:
                    lines=loc(os.path.join(dirpath,f))
                    if f.endswith(".py"):
                        py_loc+=lines
                    elif f.endswith(".html"):
                        html_loc+=lines
                    elif f.endswith(".rst"):
                        rst_loc+=lines
                    elif f.endswith(".mib"):
                        mib_loc+=lines
                    else:
                        other_loc+=lines
            r.append((dirname,py_loc,html_loc,rst_loc,mib_loc,other_loc))
        return r
            
