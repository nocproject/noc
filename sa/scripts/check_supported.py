# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CheckSupported
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from noc.sa.scripts import ReduceScript as ReduceScriptBase
import csv,os
##
## Used with get_version
## Checks returned versions against supported.csv
## and returns versions not marked as supported
##
class ReduceScript(ReduceScriptBase):
    name="CheckSupported"
    # Builds nested hashes of
    # vendor -> platform -> version
    @classmethod
    def get_supported(cls):
        r={}
        for dirpath,dirname,files in os.walk("sa/profiles/"):
            if "supported.csv" in files:
                pp=dirpath.split(os.path.sep)
                profile="%s.%s"%(pp[-2],pp[-1])
                with open(os.path.join(dirpath,"supported.csv")) as f:
                    for row in csv.reader(f):
                        if len(row)!=3:
                            continue
                        vendor,platform,version=row
                        if vendor not in r:
                            r[vendor]={}
                        if platform not in r[vendor]:
                            r[vendor][platform]={}
                        r[vendor][platform][version]=None
        return r
        
    @classmethod
    def execute(cls,task,**kwargs):
        s=cls.get_supported()
        n={}
        out="Not in supported.csv<BR/>"
        for mt in task.maptask_set.all():
            if mt.status!="C": # Ignore failed tasks
                continue
            r=mt.script_result
            if not r:
                continue
            if r["vendor"] in s and r["platform"] in s[r["vendor"]] and r["version"] in s[r["vendor"]][r["platform"]]:
                continue
            if r["vendor"] not in n:
                n[r["vendor"]]={}
            if r["platform"] not in n[r["vendor"]]:
                n[r["vendor"]][r["platform"]]={}
            n[r["vendor"]][r["platform"]][r["version"]]=None
        r=[]
        for vendor in n:
            for platform in n[vendor]:
                for version in n[vendor][platform]:
                    r+=["%s,%s,%s"%(vendor,platform,version)]
        out+="<br/>".join([x for x in sorted(r)])
        return out
