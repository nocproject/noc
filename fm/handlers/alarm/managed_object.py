# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.objectuplink import ObjectUplink
from noc.fm.models.activealarm import ActiveAlarm


def topology_rca(alarm, seen=None):
    seen = seen or set()
    if alarm.root or alarm.id in seen:
        return  # Already correlated
    seen.add(alarm.id)
    o_id = alarm.managed_object.id
    # Get neighbor objects
    neighbors = set()
    uplinks = []
    ou = ObjectUplink.objects.filter(object=o_id).first()
    if ou and ou.uplinks:
        uplinks = ou.uplinks
        neighbors.update(uplinks)
    for du in ObjectUplink.objects.filter(uplinks=o_id):
        neighbors.add(du.object)
    if not neighbors:
        return
    # Get neighboring alarms
    na = {}
    for a in ActiveAlarm.objects.filter(
        managed_object__in=list(neighbors),
        alarm_class=alarm.alarm_class.id
    ):
        na[a.managed_object.id] = a
    # Correlate with uplinks
    if uplinks and len([na[o] for o in uplinks if o in na]) == len(uplinks):
        # All uplinks are faulty
        # Correlate with the first one (shortest path)
        alarm.set_root(na[uplinks[0]])
        if hasattr(alarm, "perf_metrics"):
            alarm.perf_metrics["alarm_correlated_topology"] += 1
        # Perform correlation of uplink's alarms
        for u in uplinks:
            topology_rca(na[u], seen)
    # Correlate downlinks
    for d in na:
        if d in uplinks:
            continue
        topology_rca(na[d], seen)
