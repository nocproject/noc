# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Managed object status checks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

from noc.config import config
from noc.core.defer import call_later
# NOC modules
from noc.core.perf import metrics
from noc.fm.models.utils import get_alarm

# Delay to close out-of-ordered event
OO_CLOSE_DELAY = config.correlator.oo_close_delay

logger = logging.getLogger(__name__)


def check_down(alarm):
    """
    Try to detect out-of-ordered opening and closing event
    for ping failed
    :param alarm:
    :return:
    """
    status, last = alarm.managed_object.get_last_status()
    if not status or not last:
        return
    if alarm.timestamp >= last or not status:
        return
    # Out-of-ordered, dispose closing job
    logger.error(
        "[%s] Out of order closing event. Scheduling to close alarm after %d seconds",
        alarm.id, OO_CLOSE_DELAY
    )
    metrics["oo_pings_detected"] += 1
    call_later(
        "noc.fm.handlers.alarm.status.close_oo_alarm",
        delay=OO_CLOSE_DELAY,
        scheduler="correlator",
        pool=alarm.managed_object.pool.name,
        alarm_id=alarm.id,
        timestamp=last
    )


def close_oo_alarm(alarm_id, timestamp, *args, **kwargs):
    logger.info("[close_oo_alarm|%s] Closing alarm", alarm_id)
    alarm = get_alarm(alarm_id)
    if alarm.status != "A":
        logger.info("[close_oo_alarm|%s] Already closed, skipping",
                    alarm_id)
        return
    alarm.clear_alarm(
        message="Cleared as out-of-order",
        ts=timestamp
    )
    metrics["oo_pings_closed"] += 1
