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
from noc.core.perf import metrics
from noc.main.models.notificationgroup import NotificationGroup
from noc.core.config.base import config


logger = logging.getLogger(__name__)


def escalate(alarm_id, escalation_id, escalation_delay, *args, **kwargs):
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
        log("[%s] Alarm is not root cause, skipping", alarm_id)
        return
    #
    escalation = escalation_cache[escalation_id]
    if not escalation:
        log("Escalation %s is not found, skipping",
            escalation_id)
        return

    # Evaluate escalation chain
    mo = alarm.managed_object
    for a in escalation.escalations:
        if a.delay != escalation_delay:
            continue  # Try other type
        # Check administrative domain
        if (a.administrative_domain and
                a.administrative_domain.id not in alarm.adm_path):
            continue
        # Check severity
        if a.min_severity and alarm.severity < a.min_severity:
            continue
        # Check selector
        if a.selector and not SelectorCache.is_in_selector(mo, a.selector):
            continue
        # Check time pattern
        if a.time_pattern and not a.time_pattern.match(alarm.timestamp):
            continue
        # Render escalation message
        if not a.template:
            log("No escalation template, skipping")
            continue
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
        if ae >= config.tt_escalation_limit:
            logger.error(
                "Escalation limit exceeded (%s/%s). Skipping",
                ae, config.tt_escalation_limit
            )
            metrics["escalation_throttled"] += 1
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
            "total_services": summary_to_list(alarm.total_services, ServiceProfile),
            "tt": None
        }
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
                            subject = a.template.render_subject(**ctx)
                            body = a.template.render_body(**ctx)
                            logger.debug("[%s] Escalation message:\nSubject: %s\n%s",
                                         alarm_id, subject, body)
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
                                ctx["tt"] = "%s:%s" % (tt_system.name, tt_id)
                                alarm.escalate(ctx["tt"], close_tt=a.close_tt)
                                if tts.promote_group_tt:
                                    # Greate group TT
                                    log("Promoting to group tt")
                                    gtt = tts.create_group_tt(tt_id, alarm.timestamp)
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
                                metrics["escalation_tt_create"] += 1
                            except tts.TTError as e:
                                log("Failed to create TT: %s", e)
                                metrics["escalation_tt_fail"] += 1
                        else:
                            log("Cannot find pre reason")
                            metrics["escalation_tt_fail"] += 1
                    else:
                        log("Cannot find TT system %s", d["tt_system"])
                        metrics["escalation_tt_fail"] += 1
                else:
                    log("Cannot find TT system for %s",
                        alarm.managed_object.name)
                    metrics["escalation_tt_fail"] += 1
            if tt_id and cons_escalated:
                # Notify consequences
                for ca in cons_escalated:
                    c_tt_name, c_tt_id = ca.escalation_tt.split(":")
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
                            metrics["escalation_tt_comment"] += 1
                        except tts.TTError as e:
                            log("Failed to add comment to %s: %s",
                                ca.escalation_tt, e)
                            metrics["escalation_tt_comment_fail"] += 1
                    else:
                        log("Failed to add comment to %s: Invalid TT system",
                            ca.escalation_tt)
                        metrics["escalation_tt_comment_fail"] += 1
        # Send notification
        if a.notification_group:
            subject = a.template.render_subject(**ctx)
            body = a.template.render_body(**ctx)
            logger.debug("[%s] Notification message:\nSubject: %s\n%s",
                         alarm_id, subject, body)
            log("Sending notification to group %s", a.notification_group.name)
            a.notification_group.notify(subject, body)
            alarm.set_clear_notification(
                a.notification_group,
                a.clear_template
            )
            metrics["escalation_notify"] += 1
        #
        if a.stop_processing:
            logger.debug("Stopping processing")
            break


def notify_close(alarm_id, tt_id, subject, body, notification_group_id, close_tt=False):
    def log(message, *args):
        msg = message % args
        logger.info("[%s] %s", alarm_id, msg)

    if tt_id:
        c_tt_name, c_tt_id = tt_id.split(":")
        cts = tt_system_id_cache[c_tt_name]
        if cts:
            tts = cts.get_system()
            if close_tt:
                # Close tt
                try:
                    log("Closing TT %s", tt_id)
                    tts.close_tt(
                        c_tt_id,
                        subject=subject,
                        body=body,
                        login="correlator"
                    )
                    metrics["escalation_tt_close"] += 1
                except tts.TTError as e:
                    log("Failed to close tt %s: %s",
                        tt_id, e)
                    metrics["escalation_tt_close_fail"] += 1
            else:
                # Append comment to tt
                try:
                    log("Appending comment to TT %s", tt_id)
                    tts.add_comment(
                        c_tt_id,
                        subject=subject,
                        body=body,
                        login="correlator"
                    )
                    metrics["escalation_tt_comment"] += 1
                except tts.TTError as e:
                    log("Failed to add comment to %s: %s",
                        tt_id, e)
                    metrics["escalation_tt_comment_fail"] += 1
        else:
            log("Failed to add comment to %s: Invalid TT system",
                tt_id)
            metrics["escalation_tt_comment_fail"] += 1
    if notification_group_id:
        notification_group = notification_group_cache[notification_group_id]
        if notification_group:
            log("Sending notification to group %s", notification_group.name)
            notification_group.notify(subject, body)
            metrics["escalation_notify"] += 1
        else:
            log("Invalid notification group %s", notification_group_id)


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
    alarm.log_message("Detached from root for not recovered",
                      to_save=True)
    metrics["detached_root"] += 1
    # Trigger escalations
    AlarmEscalation.watch_escalations(alarm)


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

notification_group_cache = cachetools.TTLCache(
    CACHE_SIZE, TTL, missing=lambda x: get_item(NotificationGroup, id=x)
)
