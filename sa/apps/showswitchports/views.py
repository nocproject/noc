# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Show Switchports
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.saapplication import SAApplication


##
## Reduce task for Show Switchport application
##
def reduce_switchport(task):
    from noc.lib.app.simplereport import Report, TableSection,\
        SectionRow, TableColumn
    from noc.lib.text import list_to_ranges
    # Prepare data
    data = []
    for mt in task.maptask_set.filter(status="C"):
        data += [SectionRow("%s (%s)" % (
        mt.managed_object.name, mt.managed_object.profile_name))]
        for r in mt.script_result:
            data += [[
                r["interface"],
                r.get("description", ""),
                r["status"],
                r.get("untagged", ""),
                list_to_ranges(r.get("tagged", [])),
                ", ".join(r.get("members", []))
            ]]
        # Prepare report
    r = Report()
    r.append_section(TableSection(name="",
                                  columns=["Interface", "Description",
                                           TableColumn("Status", format="bool"),
                                           "Untagged", "Tagged", "Members"],
                                  data=data))
    return r


class ShowSwithportsApplication(SAApplication):
    title = "Show Switchports"
    menu = "Tasks | Show Switchports"
    map_task = "get_switchport"
    reduce_task = reduce_switchport
