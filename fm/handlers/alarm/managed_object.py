# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.inv.models.objectuplink import ObjectUplink
from noc.fm.models.activealarm import ActiveAlarm
from noc.core.perf import metrics
from noc.core.config.base import config
from noc.lib.dateutils import total_seconds

logger = logging.getLogger(__name__)


def topology_rca(alarm, seen=None):
    def can_correlate(a1, a2):
        return (
            not config.topology_rca_window or
            total_seconds(a1.timestamp - a2.timestamp) <= config.topology_rca_window
        )

    logger.debug("[%s] Topology RCA", alarm.id)
    seen = seen or set()
    if alarm.root or alarm.id in seen:
        logger.debug("[%s] Already correlated", alarm.id)
        return  # Already correlated
    seen.add(alarm.id)
    o_id = alarm.managed_object.id
    # Get neighbor objects
    neighbors = set()
    uplinks = ObjectUplink.uplinks_for_object(o_id)
    if uplinks:
        neighbors.update(uplinks)
    neighbors.update(ObjectUplink.neighbors_for_object(o_id))
    if not neighbors:
        logger.info("[%s] No neighbors found. Exiting", alarm.id)
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
        logger.info("[%s] All uplinks are faulty. Correlating", alarm.id)
        for u in uplinks:
            a = na[u]
            if can_correlate(alarm, a):
                logger.info("[%s] Set root to %s", alarm.id, a.id)
                alarm.set_root(a)
                metrics["alarm_correlated_topology"] += 1
                break
    # Correlate neighbors' alarms
    for d in na:
        topology_rca(na[d], seen)
    logger.debug("[%s] Correlation completed", alarm.id)
