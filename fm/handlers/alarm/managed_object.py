# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from threading import Lock
## Third-party modules
from mongoengine.queryset import Q
## NOC modules
from noc.fm.models.activealarm import ActiveAlarm
from noc.core.perf import metrics
from noc.core.config.base import config
from noc.lib.dateutils import total_seconds

logger = logging.getLogger(__name__)

rca_lock = Lock()


def _topology_rca(alarm, seen=None):
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
    # Get neighboring alarms
    na = {}
    # Downlinks
    q = Q(
        alarm_class=alarm.alarm_class.id,
        uplinks=alarm.managed_object.id
    )
    # Uplinks
    # @todo: Try to use $graphLookup to find affinity alarms
    if alarm.uplinks:
        q |= Q(alarm_class=alarm.alarm_class.id,
               managed_object__in=list(alarm.uplinks))
    for a in ActiveAlarm.objects.filter(q):
        na[a.managed_object.id] = a
    # Correlate with uplinks
    if alarm.uplinks and len([na[o] for o in alarm.uplinks if o in na]) == len(alarm.uplinks):
        # All uplinks are faulty
        # uplinks are ordered according to path length
        # Correlate with first applicable
        logger.info("[%s] All uplinks are faulty. Correlating", alarm.id)
        for u in alarm.uplinks:
            a = na[u]
            if can_correlate(alarm, a):
                logger.info("[%s] Set root to %s", alarm.id, a.id)
                alarm.set_root(a)
                metrics["alarm_correlated_topology"] += 1
                break
    # Correlate neighbors' alarms
    for d in na:
        _topology_rca(na[d], seen)
    logger.debug("[%s] Correlation completed", alarm.id)


def topology_rca(alarm):
    with rca_lock:
        _topology_rca(alarm)
