# ---------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.maintenance.models.maintenance import Maintenance
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.ttsystem import TTSystem
from noc.core.tt.base import TTSystemCtx
from noc.core.tt.types import EscalationItem as ECtxItem
from noc.core.perf import metrics

logger = logging.getLogger(__name__)


def start_maintenance(maintenance_id):
    logger.info("[%s] Start maintenance", maintenance_id)
    m = Maintenance.get_by_id(maintenance_id)
    if not m:
        logger.info("[%s] Not found, skipping")
        return
    if not m.escalate_managed_object:
        logger.info("[%s] No managed object to escalate", maintenance_id)
        return
    if m.escalation_tt:
        logger.info("[%s] Already escalated as TT %s", maintenance_id, m.escalation_tt)
        return
    # Get external TT system
    tts_id = m.escalate_managed_object.tt_system_id
    if not tts_id:
        logger.info(
            "[%s] No TT mapping for object %s(%s)",
            maintenance_id,
            m.escalate_managed_object.name,
            m.escalate_managed_object.address,
        )
        return
    tt_system = m.escalate_managed_object.tt_system

    if not tt_system:
        logger.info("[%s] Cannot find TT system '%s'", maintenance_id, m.escalate_managed_object)
        return
    e_ctx_items = [
        ECtxItem(id=m.escalate_managed_object.id, tt_id=m.escalate_managed_object.tt_system_id)
    ]
    SQL = """SELECT id, name, tt_system_id
        FROM sa_managedobject
        WHERE affected_maintenances @> '{"%s": {}}';""" % str(
        maintenance_id
    )
    for mo in ManagedObject.objects.raw(SQL):
        logger.info("[%s] Appending object %s to TT", maintenance_id, mo)
        e_ctx_items.append(ECtxItem(id=mo.id, tt_id=mo.tt_system_id))
    logger.info("[%s] Creating TT", maintenance_id)
    with TTSystemCtx(
        tt_system=tt_system.get_system(),
        queue=m.escalate_managed_object.tt_queue if m.escalate_managed_object.tt_queue else 1,
        reason="0",
        login="correlator",
        timestamp=m.start,
        items=e_ctx_items,
    ) as ctx:
        # ctx.add_items(e_ctx_items)
        ctx.create(subject=m.subject, body=m.description or m.subject)
    r = ctx.get_result()
    if not r.is_ok or not r.document:
        logger.error("[%s] Failed to escalate: %s", maintenance_id, r.error)
        metrics["maintenance_tt_fail"] += 1
    logger.info("[%s] TT %s created", maintenance_id, r.document)
    if r.document and not m.escalation_tt:
        m.escalation_tt = f"{m.escalate_managed_object.tt_system.name}:{r.document}"
        m.save()
    metrics["maintenance_tt_create"] += 1


def close_maintenance(maintenance_id):
    logger.info("[%s] Close maintenance", maintenance_id)
    m = Maintenance.get_by_id(maintenance_id)
    if not m:
        logger.info("[%s] Not found, skipping", maintenance_id)
        return
    if not m.escalation_tt:
        logger.info("[%s] Not escalated, skipping", maintenance_id)
        return
    tts_name, tt_id = m.escalation_tt.split(":", 1)
    tts = TTSystem.get_by_name(tts_name)
    if not tts:
        logger.error("[%s] TT system '%s' is not found", maintenance_id, tts_name)
        return
    with TTSystemCtx(
        tt_system=tts,
        queue=m.escalate_managed_object.tt_queue if m.escalate_managed_object.tt_queue else 1,
        reason="0",
        login="correlator",
        timestamp=m.start,
    ) as ctx:
        logger.info("[%s] Closing TT %s", maintenance_id, tt_id)
        ctx.close(subject="Closed", body="Closed")
    r = ctx.get_result()
    if r.is_ok:
        metrics["maintenance_tt_close"] += 1
    else:
        logger.error("[%s] Failed to close TT %s: %s", maintenance_id, tt_id, r.error)
        metrics["maintenance_tt_close_fail"] += 1
