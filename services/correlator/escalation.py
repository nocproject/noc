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
import datetime
import operator
## NOC modules
from noc.fm.models.utils import get_alarm
from noc.fm.models.ttsystem import TTSystem
from noc.sa.models.selectorcache import SelectorCache
from noc.inv.models.extnrittmap import ExtNRITTMap
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm


logger = logging.getLogger(__name__)


def escalate(alarm_id, escalation_id, escalation_delay, tt_escalation_limit):
    def log(message, *args):
        msg = message % args
        logger.info("[%s] %s", alarm_id, msg)
        alarm.log_message(msg, to_save=True)

    def summary_to_list(summary, model):
        r = []
        for k in summary:
            p = model.get_by_id(k.profile)
            if not p or getattr(p, "show_in_summary", True) == False:
                continue
            r += [{
                "profile": p.name,
                "summary": k.summary
            }]
        return sorted(r, key=lambda x: -x["summary"])

    logger.info("[%s] Performing escalations", alarm_id)
    alarm = get_alarm(alarm_id)
    if alarm is None:
        logger.info("[%s] Missing alarm, skipping", alarm_id)
        return
    if alarm.status == "C":
        logger.info("[%s] Alarm is closed, skipping", alarm_id)
        return
    if alarm.root:
        log("Alarm is not root cause, skipping")
        return
    #
    escalation = escalation_cache[escalation_id]
    if not escalation:
        log("Escalation %s is not found, skipping", escalation_id)
        return

    # Evaluate escalation chain
    mo = alarm.managed_object
    for a in escalation.escalations:
        if a.delay != escalation_delay:
            continue  # Try other type
        # Check administrative domain
        if (
            a.administrative_domain and
            mo.administrative_domain.id != a.administrative_domain.id
        ):
            continue
        # Check selector
        if a.selector and not SelectorCache.is_in_selector(mo, a.selector):
            continue
        # Render escalation message
        if not a.template:
            log("No escalation template, skipping")
            return
        # Check global limits
        ets = datetime.datetime.now() - datetime.timedelta(seconds=60)
        ae = ActiveAlarm._get_collection().find({
            "escalation_ts": {
                "$gte": ets
            }
        }).count()
        ae += ArchivedAlarm._get_collection().find({
            "escalation_ts": {
                "$gte": ets
            }
        }).count()
        if ae >= tt_escalation_limit:
            logger.error(
                "Escalation limit exceeded (%s/%s). Skipping",
                ae, tt_escalation_limit
            )
            return
        # Check whether consequences has escalations
        cons_escalated = sorted(alarm.iter_escalated(),
                                key=operator.attrgetter("timestamp"))
        affected_objects = sorted(alarm.iter_affected(),
                                  key=operator.attrgetter("name"))
        #
        ctx = {
            "alarm": alarm,
            "affected_objects": affected_objects,
            "cons_escalated": cons_escalated,
            "total_objects": summary_to_list(alarm.total_objects, ManagedObjectProfile),
            "total_subscribers": summary_to_list(alarm.total_subscribers, SubscriberProfile),
            "total_services": summary_to_list(alarm.total_services, ServiceProfile)
        }
        subject = a.template.render_subject(**ctx)
        body = a.template.render_body(**ctx)
        logger.debug("[%s] Escalation message:\nSubject: %s\n%s",
                     alarm_id, subject, body)
        # Send notification
        if a.notification_group:
            log("Sending notification to group %s", a.notification_group.name)
            a.notification_group.notify(subject, body)
        # Escalate to TT
        if a.create_tt:
            tt_id = None
            if alarm.escalation_tt:
                log(
                    "Already escalated with TT #%s",
                    alarm.escalation_tt
                )
            else:
                # Get external TT system
                d = ExtNRITTMap._get_collection().find_one({
                    "managed_object": mo.id
                })
                if d:
                    tt_system = tt_system_cache[d["tt_system"]]
                    if tt_system:
                        pre_reason = escalation.get_pre_reason(tt_system)
                        if pre_reason is not None:
                            log("Creating TT in system %s", tt_system.name)
                            tts = tt_system.get_system()
                            try:
                                tt_id = tts.create_tt(
                                    queue=d["queue"],
                                    obj=d["remote_id"],
                                    reason=pre_reason,
                                    subject=subject,
                                    body=body,
                                    login="correlator"
                                )
                                alarm.escalate(
                                    "%s:%s" % (tt_system.name, tt_id)
                                )
                                if tts.promote_group_tt:
                                    # Greate group TT
                                    log("Promoting to group tt")
                                    gtt = tts.create_group_tt(tt_id)
                                    # Add objects
                                    objects = dict(
                                        (o.id, o.name)
                                        for o in alarm.iter_affected()
                                    )
                                    for d in ExtNRITTMap._get_collection().find({
                                        "managed_object": {
                                            "$in": list(objects)
                                        }
                                    }):
                                        log(
                                            "Appending object %s to group tt %s",
                                            objects[d["managed_object"]],
                                            gtt
                                        )
                                        tts.add_to_group_tt(
                                            gtt,
                                            d["remote_id"]
                                        )
                            except tts.TTError as e:
                                log("Failed to create TT: %s", e)
                        else:
                            log("Cannot find pre reason")
                    else:
                        log("Cannot find TT system %s", d["tt_system"])
                else:
                    log("Cannot find TT system for %s",
                        alarm.managed_object.name)
            if tt_id and cons_escalated:
                # Notify consequences
                for a in cons_escalated:
                    c_tt_name, c_tt_id = a.escalation_tt.split(":")
                    cts = tt_system_id_cache[c_tt_name]
                    if cts:
                        tts = cts.get_system()
                        try:
                            log("Appending comment to TT %s", tt_id)
                            tts.add_comment(
                                c_tt_id,
                                body="Covered by TT %s" % tt_id,
                                login="correlator"
                            )
                        except tts.TTError as e:
                            log("Failed to add comment to %s: %s",
                                a.escalation_tt, e)
                    else:
                        log("Failed to add comment to %s: Invalid TT system",
                            a.escalation_tt)
        #
        if a.stop_processing:
            logger.debug("Stopping processing")
            break


def get_item(model, **kwargs):
    if not id:
        return None
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

TTL = 60
CACHE_SIZE = 256

escalation_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(AlarmEscalation, id=x)
)

tt_system_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(TTSystem, id=x)
)

tt_system_id_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(TTSystem, name=x)
)
