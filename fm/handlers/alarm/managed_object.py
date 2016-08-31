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
from noc.core.perf import metrics
from noc.core.config.base import config
from noc.lib.dateutils import total_seconds


def topology_rca(alarm, seen=None):
    def can_correlate(a1, a2):
        return (
            not config.topology_rca_window or
            total_seconds(a1.timestamp - a2.timestamp) <= config.topology_rca_window
        )

    seen = seen or set()
    seen.add(alarm.id)
    if alarm.root or alarm.id in seen:
        return  # Already correlated
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
        # uplinks are ordered according to path length
        # Correlate with first applicable
        for u in uplinks:
            a = na[u]
            if can_correlate(alarm, a):
                alarm.set_root(na[uplinks[0]])
                metrics["alarm_correlated_topology"] += 1
                break
    # Correlate neighbors' alarms
    for d in na:
        topology_rca(na[d], seen)
