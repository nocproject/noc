# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Escalation
##----------------------------------------------------------------------
## Copyright (C) 2007-2016, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import cachetools
## NOC modules
from noc.core.defer import call_later
from noc.fm.models.utils import get_alarm
from noc.main.models.template import Template
from noc.main.models.notificationgroup import NotificationGroup
from noc.fm.models.ttsystem import TTSystem

logger = logging.getLogger(__name__)


class Escalation(object):
    def __init__(self, delay, notification_group,
                 tt_system, tt_queue, template):
        self.delay = int(delay)
        if self.notification_group:
            self.notification_group = notification_group.id
        else:
            self.notification_group = None
        if self.tt_system:
            self.tt_system = tt_system.id
            self.tt_queue = tt_queue
        else:
            self.tt_system = None
            self.tt_queue = None
        self.template = template.id

    def watch(self, alarm):
        """
        Watch for further escalations
        """
        logger.info("[%s] Watching for possible escalation", alarm.id)
        call_later(
            "noc.services.correlator.escalation.escalate",
            delay=self.delay,
            alarm_id=alarm.id,
            notificaiton_group_id=self.notification_group,
            tt_system_id=self.tt_system,
            tt_queue_id=self.tt_queue,
            template_id=self.template
        )


def get_item(model, id):
    try:
        return model.objects.get(id=id)
    except model.DoesNotExist:
        return None

TTL = 60
CACHE_SIZE = 256

template_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(Template, x)
)
notification_group_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(NotificationGroup, x)
)
tt_system_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(TTSystem, x)
)


def escalate(alarm_id, notification_group_id=None, tt_system_id=None,
             tt_queue=None, template_id=None):
    logger.info("[%s] Performing escalations", alarm_id)
    alarm = get_alarm(alarm_id)
    if alarm is None:
        logger.info("[%s] Missing alarm, skipping", alarm_id)
        return
    if alarm.status == "C":
        logger.info("[%s] Alarm is closed, skipping", alarm_id)
        return
    if alarm.root:
        logger.info("[%s] Alarm is not root cause, skipping", alarm_id)
        return
    if not template_id:
        logger.info("[%s] Missed template, skipping", alarm_id)
        return
    if not notification_group_id and not tt_system_id:
        logger.info("[%s] Neither TT system nor notification group specified, skipping", alarm_id)
        return
    template = template_cache[template_id]
    if not template:
        logger.info("[%s] Template not found, skipping", alarm_id)
        return
    notification_group = notification_group_cache[notification_group_id]
    tt_system = tt_system_cache[tt_system_id]
    if not notification_group and not tt_system:
        logger.info("[%s] Cannot resolve notification group nor tt system. Skipping", alarm_id)
        return
    ctx = {
        "alarm": alarm
    }
    subject = template.render_subject(**ctx)
    body = template.render_body(**ctx)
    logger.debug("[%s] Escalation message:\nSubject: %s\n%s", alarm_id, subject, body)
    tt_id = "NOTIFY"
    if notification_group:
        notification_group.notify(subject, body)
    # @todo: Escalate to TT System
    # Mark alarm as escalated
    alarm.escalate(tt_id)
