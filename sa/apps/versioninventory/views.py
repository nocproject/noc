# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## <<DESCRIPTION>>
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
##
## Reduce handler to show version report
##
def reduce(task):
    from noc.lib.app.simplereport import Report,TableSection,SectionRow
    # Fetch data
    ad={}
    summary={}
    for mt in task.maptask_set.all():
        adn=mt.managed_object.administrative_domain.name
        if adn not in ad:
            ad[adn]=[]
        r=mt.script_result
        if mt.status=="C":
            # Completed tasks
            ad[adn]+=[(mt.managed_object.name,r["vendor"],r["platform"],r["version"])]
            if (r["vendor"],r["platform"],r["version"]) in summary:
                summary[(r["vendor"],r["platform"],r["version"])]+=1
            else:
                summary[(r["vendor"],r["platform"],r["version"])]=1
        else:
            # Failed tasks
            ad[adn]+=[(mt.managed_object.name,"-","-","-")]
    # Prepare data
    data=[]
    for adn in sorted(ad.keys()):
        data+=[SectionRow(name=adn)]
        data+=sorted(ad[adn],lambda x,y:cmp(x[0],y[0]))
    # Build report
    report=Report()
    # Object versions
    t=TableSection(name="result",columns=["Object","Vendor","Plaform","Version"],data=data,enumerate=True)
    report.append_section(t)
    # Version summary
    summary=sorted([(vp[0],vp[1],vp[2],c) for vp,c in summary.items()],lambda x,y:-cmp(x[3],y[3]))
    t=TableSection(name="summary",columns=["Vendor","Platform","Version","Count"],data=summary,enumerate=True)
    report.append_section(t)
    return report
##
##
##
class VersionInventoryApplication(SAApplication):
    title="Version Inventory"
    menu="Tasks | Version Inventory"
    reduce_task=reduce
    map_task="get_version"
    timeout=60
