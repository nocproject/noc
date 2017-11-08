# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Segment handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import six
from noc.fm.models.activealarm import ActiveAlarm
# NOC modules
from noc.sa.models.objectdata import ObjectData

logger = logging.getLogger(__name__)


def set_segment_redundancy(alarm):
    """
    Set lost_redundancy to segment when redundant object is down
    :param alarm:
    :return:
    """
    if alarm.root:
        return  # Already changed by root cause
    mo = alarm.managed_object
    seg = mo.segment
    if seg.is_redundant and not seg.lost_redundancy:
        u = mo.data.uplinks
        if len(u) > 1:
            logger.info("[%s] Redundancy lost for %s", alarm.id, seg.name)
            seg.set_lost_redundancy(True)


def check_segment_redundancy(alarm):
    """
    Reset lost_redundancy from segment when all redundant objects
    are up
    :param alarm:
    :return:
    """
    mo = alarm.managed_object
    seg = mo.segment
    if not seg.is_redundant or not seg.lost_redundancy:
        return
    u = mo.data.uplinks
    if len(u) < 2:
        return
    seg_objects = [long(x) for x in seg.managed_objects.values_list("id", flat=True)]
    alarms = [
        d["managed_object"]
        for d in ActiveAlarm._get_collection().find({
            "managed_object": {"$in": seg_objects}
        }, {"_id": 0, "managed_object": 1})
        if d["managed_object"] != mo.id
    ]
    uplinks = ObjectData.uplinks_for_objects(alarms)
    if not any(x for x in six.itervalues(uplinks) if len(x) > 1):
        logger.info("[%s] Redundancy recovered for %s", alarm.id, seg.name)
        seg.set_lost_redundancy(False)
