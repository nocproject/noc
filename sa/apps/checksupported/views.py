# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Check profiles' supported.csv
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
##
## Reduce task to check supported.csv
##
def reduce_supported(task):
    import csv,os

    loaded_profiles=set()
    supported_versions=set()
    new_versions=set()
    
    for mt in task.maptask_set.all():
        if mt.status!="C":
            continue
        profile=mt.managed_object.profile_name
        if profile not in loaded_profiles:
            # Read profile's supported CSV
            v,o=profile.split(".")
            path=os.path.join("sa","profiles",v,o,"supported.csv")
            if os.path.exists(path):
                f=open(path)
                for row in csv.reader(f):
                    if len(row)!=3:
                        continue
                    supported_versions.add(",".join(row))
                f.close()
            loaded_profiles.add(profile)
        r=mt.script_result
        v=",".join([r["vendor"],r["platform"],r["version"]])
        # Update new versions if not exists
        if v not in supported_versions:
            new_versions.add(v)
    # Return result
    return "Not in supported.csv<br/>"+"<br/>\n".join(sorted(new_versions))
##
##
##
class CheckSupportedApplication(SAApplication):
    title="Check supported.csv"
    menu="Tasks | Check supported.csv"
    reduce_task=reduce_supported
    map_task="get_version"
    timeout=180
