# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Lines of Code  Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import glob
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn, SectionRow
from noc import settings


class ReportLOC(SimpleReport):
    title = "Lines Of Code"

    def get_data(self,**kwargs):
        def lines(path):
            """
            Count lines in file
            """
            with open(path) as f:
                return len(f.read().split("\n"))

        def dir_loc(path):
            """
            Scan directory and count lines of code
            """
            py_loc = 0
            html_loc = 0
            tests_loc = 0
            for dirpath, dirnames, filenames in os.walk(path):
                in_tests = "tests" in dirpath.split(os.sep)
                for f in filenames:
                    path=os.path.join(dirpath,f)
                    if f.endswith(".py"):
                        if in_tests:
                            tests_loc += lines(path)
                        else:
                            py_loc += lines(path)
                    elif f.endswith(".html"):
                        html_loc += lines(path)
            return py_loc, html_loc, tests_loc

        data=[]
        # Scan modules
        for m in [m for m in settings.INSTALLED_APPS if m.startswith("noc.")]:
            m=m[4:]
            module_name=__import__("noc.%s"%m,{},{},["MODULE_NAME"]).MODULE_NAME
            data+=[SectionRow(module_name)]
            # Scan models
            py_loc=lines(os.path.join(m,"models.py"))
            _, _, tests_loc = dir_loc(os.path.join(m, "tests"))
            data+=[["Model","models.py",py_loc,0,tests_loc]]
            # Scan Migrations
            py_loc, _, _ = dir_loc(os.path.join(m, "migrations"))
            data+=[["Migrations","",py_loc,0,0]]
            # Scan Management
            for dirpath,dirnames,filenames in os.walk(os.path.join(m,"management","commands")):
                for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py"]:
                    py_loc=lines(os.path.join(dirpath,f))
                    data+=[["Management",f[:-3],py_loc,0,0]]
            # Scan Templates
            py_loc,html_loc,_=dir_loc(os.path.join(m,"templates"))
            data+=[["Templates","",py_loc,html_loc,0]]
            # Scan applications
            for app in [d for d in os.listdir(os.path.join(m,"apps")) if not d.startswith(".")]:
                app_path=os.path.join(m,"apps",app)
                if not os.path.isdir(app_path):
                    continue
                py_loc=0
                html_loc=0
                tests_loc=0
                for dirpath,dirnames,filenames in os.walk(app_path):
                    if os.sep+"tests" in dirpath:
                        for f in [f for f in filenames if f.endswith(".py")]:
                            tests_loc+=lines(os.path.join(dirpath,f))
                    else:
                        for f in [f for f in filenames if f.endswith(".py")]:
                            py_loc+=lines(os.path.join(dirpath,f))
                        for f in [f for f in filenames if f.endswith(".html")]:
                            html_loc+=lines(os.path.join(dirpath,f))
                data+=[["Application","%s.%s"%(m,app),py_loc,html_loc,tests_loc]]
            # Scan Profiles
            if m=="sa":
                for d in glob.glob("sa/profiles/*/*"):
                    if not os.path.isdir(d):
                        continue
                    pp=d.split(os.sep)
                    profile=".".join(pp[-2:])
                    py_loc,html_loc,tests_loc=dir_loc(d)
                    data+=[["Profile",profile,py_loc,html_loc,tests_loc]]
            # Scan other
            py_loc=0
            for dirpath,dirnames,filenames in os.walk(m):
                if os.sep+"tests" in dirpath or os.sep+"templates" in dirpath or os.sep+"apps" in dirpath\
                    or os.sep+"management" in dirpath or os.sep+"migrations" in dirpath:
                    continue
                for f in [f for f in filenames if f.endswith(".py") if f!="models.py"]:
                    py_loc+=lines(os.path.join(dirpath,f))
            data+=[["Other","",py_loc,0,0]]
        return self.from_dataset(title=self.title,
            columns=[
                "Type",
                TableColumn("Name",total_label="Total"),
                TableColumn("Python",format="numeric",align="right",total="sum"),
                TableColumn("HTML",format="numeric",align="right",total="sum"),
                TableColumn("Tests",format="numeric",align="right",total="sum"),
            ],
            data=data)
