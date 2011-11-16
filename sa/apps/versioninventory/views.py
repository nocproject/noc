# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.version_inventory application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.saapplication import SAApplication


def reduce(task):
    """
    Reduce handler to show version report
    :param task: ReduceTask instance
    :return:
    """
    from noc.lib.app.simplereport import Report, TableSection, SectionRow
    # Fetch data
    ad = {}  # administrative domain -> data
    summary = {}  # (vendor, platform, version) -> count
    attrs = {}  # Attribute, count
    # First pass - count summary and attributes
    for mt in task.maptask_set.all():
        adn = mt.managed_object.administrative_domain.name
        if adn not in ad:
            ad[adn] = []
        if mt.status == "C":
            r = mt.script_result
            # Update summary
            if (r["vendor"], r["platform"], r["version"]) in summary:
                summary[(r["vendor"], r["platform"], r["version"])] += 1
            else:
                summary[(r["vendor"], r["platform"], r["version"])] = 1
            # Update attributes count
            if "attributes" in r:
                for k in r["attributes"]:
                    if k in attrs:
                        attrs[k] += 1
                    else:
                        attrs[k] = 1
    # Prepare a list of additional attributes
    a_fail = ("-", ) * (len(attrs) + 3)
    a_list = sorted(attrs.keys(), lambda x, y: cmp(attrs[y], attrs[x]))
    # Second pass - fill data
    for mt in task.maptask_set.all():
        adn = mt.managed_object.administrative_domain.name
        r = mt.script_result
        if mt.status == "C":
            # Completed tasks
            s = (mt.managed_object.name,
                 r["vendor"], r["platform"], r["version"])
            if "attributes" in r:
                s += tuple([r["attributes"].get(k, "-") for k in a_list])
            else:
                s += ("-", ) * len(a_list)
            ad[adn] += [s]
        else:
            # Failed tasks
            ad[adn] += [(mt.managed_object.name,) + a_fail]
    # Prepare data
    data = []
    for adn in sorted(ad.keys()):
        data += [SectionRow(name=adn)]
        data += sorted(ad[adn], lambda x, y: cmp(x[0], y[0]))
    # Build report
    report = Report()
    # Object versions
    t = TableSection(name="result",
                     columns=["Object", "Vendor", "Plaform",
                              "Version"] + a_list,
                     data=data, enumerate=True)
    report.append_section(t)
    # Version summary
    summary = sorted([(vp[0], vp[1], vp[2], c) for vp, c in summary.items()],
                     lambda x, y: -cmp(x[3], y[3]))
    t = TableSection(name="summary",
                     columns=["Vendor", "Platform", "Version", "Count"],
                     data=summary, enumerate=True)
    report.append_section(t)
    return report


class VersionInventoryApplication(SAApplication):
    title = "Version Inventory"
    menu = "Tasks | Version Inventory"
    reduce_task = reduce
    map_task = "get_version"
