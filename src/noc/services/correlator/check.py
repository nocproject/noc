# ---------------------------------------------------------------------
# Various checks
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.fm.models.utils import get_alarm
from noc.core.perf import metrics

logger = logging.getLogger(__name__)


def check_close_consequence(alarm_id):
    logger.info("[%s] Checking close", alarm_id)
    alarm = get_alarm(alarm_id)
    if alarm is None:
        logger.info("[%s] Missing alarm, skipping", alarm_id)
        return
    if alarm.status == "C":
        logger.info("[%s] Alarm is closed. Check passed", alarm_id)
        return
    # Detach root
    logger.info("[%s] Alarm is active. Detaching root", alarm_id)
    alarm.root = None
    alarm.log_message("Detached from root for not recovered", to_save=True)
    metrics["detached_root"] += 1
