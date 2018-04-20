# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Switchport Validation Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.saapplication import SAApplication


##
## Reduce task for switchport validation
##
def switchport_validation_reduce(task):
    from noc.lib.app.simplereport import Report, TableSection, SectionRow
    from noc.lib.text import list_to_ranges

    switchports = {} # object -> interface -> (description, set of vlans)
    macs = {}        # object -> interface -> set of vlans
    # Collect data
    for mt in task.maptask_set.filter(status="C"):
        o = mt.managed_object
        if mt.map_script.endswith(".get_mac_address_table"):
            # Populate macs
            macs[o] = {}
            for m in mt.script_result:
                for i in m["interfaces"]:
                    if i not in macs[o]:
                        macs[o][i] = set()
                    macs[o][i].add(m["vlan_id"])
        elif mt.map_script.endswith(".get_switchport"):
            # Populate switchports
            switchports[o] = {}
            for p in mt.script_result:
                if not p["status"]:
                    # Skip ports in shutdown
                    continue
                i = p["interface"]
                if i not in switchports[o]:
                    switchports[o][i] = (p.get("description", ""), set())
                if "untagged" in p and p["untagged"]:
                    switchports[o][i][1].add(p["untagged"])
                if p["tagged"]:
                    switchports[o][i][1].update(p["tagged"])
        else:
            raise Exception("Inconsistent map task")
    if not macs or not switchports:
        return "Failed to retrieve the data!!!"
        # Process data
    data = []
    for o in switchports:
        if o not in macs or not macs[o]:
            continue
        # Find inconsistent ports
        inconsistent_ports = [] # (port, swtichport vlans, excessive vlans)
        for i in switchports[o]:
            if i not in macs[o]:
                # No mac data for port
                inconsistent_ports += [
                    (i, switchports[o][i][0], switchports[o][i][1], None)]
            else:
                # Remove intersection
                v = switchports[o][i][1] - macs[o][i]
                if v:
                    inconsistent_ports += [
                        (i, switchports[o][i][0], switchports[o][i][1], v)]
        # Add to data if inconsistent ports found
        if inconsistent_ports:
            data += [SectionRow(o.name)]
            data += [(p, d, list_to_ranges(v),
                      list_to_ranges(e) if e is not None else "No MACs found")
            for p, d, v, e in
            sorted(inconsistent_ports, lambda x, y:cmp(x[0], y[0]))]
        #
    if not data:
        return "Failed to retrieve data!!!"
    # Build report
    r = Report()
    r.append_section(TableSection("", columns=["Port", "Description",
                                               "Switchport VLANs",
                                               "Excessive VLANs"], data=data))
    return r

##
##
##
class SwitchportValidationAppplication(SAApplication):
    title = "Switchport Validation"
    menu = "Tasks | Switchport Validation"
    reduce_task = switchport_validation_reduce
    map_task = ["get_mac_address_table", "get_switchport"]
