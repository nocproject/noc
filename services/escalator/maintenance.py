# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
# NOC modules
from noc.maintainance.models.maintainance import Maintainance
from noc.fm.models.ttsystem import TTSystem
from noc.core.perf import metrics
from noc.inv.models.extnrittmap import ExtNRITTMap

logger = logging.getLogger(__name__)


def start_maintenance(maintenance_id):
    logger.info("[%s] Start maintenance")
    m = Maintainance.get_by_id(maintenance_id)
    if not m:
        logger.info("[%s] Not found, skipping")
        return
    if not m.escalate_managed_object:
        logger.info("[%s] No managed object to escalate",
                    maintenance_id)
        return
    if m.escalation_tt:
        logger.info("[%s] Already escalated as TT %s",
                    maintenance_id, m.escalation_tt)
        return
    # Get external TT system
    d = ExtNRITTMap._get_collection().find_one({
        "managed_object": m.escalate_managed_object.id
    })
    if not d:
        logger.info("[%s] No TT mapping for object %s(%s)",
                    maintenance_id, m.escalate_managed_object.name,
                    m.escalate_managed_object.address)
        return
    tt_system = TTSystem.get_by_id(d["tt_system"])
    if not tt_system:
        logger.info("[%s] Cannot find TT system '%s'",
                    maintenance_id, d["tt_system"])
        return
    tts = tt_system.get_system()
    try:
        logger.info("[%s] Creating TT", maintenance_id)
        tt_id = tts.create_tt(
            queue=1,
            obj=d["remote_id"],
            reason=0,
            subject=subject,
            body=body,
            login="correlator",
            timestamp=m.start
        )
        logger.info("[%s] TT %s created", maintenance_id, tt_id)
        if tts.promote_group_tt:
            gtt = tts.create_group_tt(tt_id, m.start)
            d = Maintainance._get_collection().find_one({
                "_id": m.id
            }, {
                "_id": 0,
                "affected_objects": 1
            })
            if d:
                objects = [x["object"] for x in d["affected_objects"]]
                for d in ExtNRITTMap._get_collection().find({
                    "managed_object": {
                        "$in": list(objects)
                    },
                    "tt_system": tt_system.id
                }):
                    logger.info(
                        "[%s] Appending object %s to group TT %s",
                        maintenance_id,
                        d["managed_object"],
                        gtt
                    )
                    tts.add_to_group_tt(
                        gtt,
                        d["remote_id"]
                    )
        metrics["maintenance_tt_create"] += 1
    except tts.TTError as e:
        logger.error("[%s] Failed to escalate: %s", maintenance_id, e)
        metrics["maintenance_tt_fail"] += 1


def close_maintenance(maintenance_id):
    logger.info("[%s] Start maintenance")
    m = Maintainance.get_by_id(maintenance_id)
    if not m:
        logger.info("[%s] Not found, skipping", maintenance_id)
        return
    if not m.escalation_tt:
        logger.info("[%s] Not escalated, skipping", maintenance_id)
        return
    tts_name, tt_id = m.escalation_tt.split(":", 1)
    tts = TTSystem.get_by_name(tts_name)
    if not tts:
        logger.error("[%s] TT system '%s' is not found",
                     maintenance_id, tts_name)
        return
    try:
        logger.info("[%s] Closing TT %s", maintenance_id, tt_id)
        tts.close_tt(
            m.escalation_tt,
            subject="Closed",
            body="Closed",
            login="correlator"
        )
        metrics["maintenance_tt_close"] += 1
    except tts.TTError as e:
        logger.error("[%s] Failed to close TT %s: %s",
                     maintenance_id, tt_id, e)
        metrics["maintenance_tt_close_fail"] += 1
