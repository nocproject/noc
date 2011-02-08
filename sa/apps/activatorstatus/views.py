# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator Status
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.saapplication import SAApplication
##
def reduce_status(task):
    from noc.lib.app.simplereport import Report,TableSection,TableColumn
    data=[]
    for mt in task.maptask_set.filter(status="C"):
        for r in mt.script_result:
            data+=[(r["name"], r["status"], r["members"])]
    report=Report()
    t=TableSection(name="status",columns=["Activator",TableColumn("Status",format="bool"),TableColumn("Members", align="right")],
        data=data,enumerate=True)
    report.append_section(t)
    return report
##
##
##
class ActivatorStatusApplication(SAApplication):
    title="Activator Status"
    menu="Tasks | Activator Status"
    reduce_task=reduce_status
    map_task="get_activator_status"
    timeout=10
    objects=["SAE"]
