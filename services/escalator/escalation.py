# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Escalation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import cachetools
import datetime
import operator
import threading
# NOC modules
from noc.fm.models.utils import get_alarm
from noc.fm.models.ttsystem import TTSystem
from noc.sa.models.selectorcache import SelectorCache
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.core.perf import metrics
from noc.main.models.notificationgroup import NotificationGroup
from noc.maintenance.models.maintenance import Maintenance
from noc.config import config
from noc.core.tt.error import TTError, TemporaryTTError
from noc.core.scheduler.job import Job
from noc.core.span import Span, PARENT_SAMPLE


logger = logging.getLogger(__name__)

RETRY_TIMEOUT = config.escalator.retry_timeout
# @fixme have to be checked
RETRY_DELTA = 60 / max(config.escalator.tt_escalation_limit - 1, 1)

retry_lock = threading.Lock()
next_retry = datetime.datetime.now()


def escalate(alarm_id, escalation_id, escalation_delay,
             *args, **kwargs):
    def log(message, *args):
        msg = message % args
        logger.info("[%s] %s", alarm_id, msg)
        alarm.log_message(msg, to_save=True)

    def summary_to_list(summary, model):
        r = []
        for k in summary:
            p = model.get_by_id(k.profile)
            if not p or getattr(p, "show_in_summary", True) is False:
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
        metrics["escalation_missed_alarm"] += 1
        return
    if alarm.status == "C":
        logger.info("[%s] Alarm is closed, skipping", alarm_id)
        metrics["escalation_already_closed"] += 1
        return
    if alarm.root:
        log("[%s] Alarm is not root cause, skipping", alarm_id)
        metrics["escalation_alarm_is_not_root"] += 1
        return
    #
    escalation = escalation_cache[escalation_id]
    if not escalation:
        log("Escalation %s is not found, skipping",
            escalation_id)
        metrics["escalation_not_found"] += 1
        return
    if alarm.managed_object.tt_system:
        sample = alarm.managed_object.tt_system.telemetry_sample
    else:
        sample = PARENT_SAMPLE
    with Span(client="escalator", sample=sample) as ctx:
        alarm.set_escalation_context()
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
            # @todo: Move into escalator service
            # @todo: Process per-ttsystem limits
            ets = datetime.datetime.now() - datetime.timedelta(seconds=config.escalator.ets)
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
            if ae >= config.escalator.tt_escalation_limit:
                logger.error(
                    "Escalation limit exceeded (%s/%s). Skipping",
                    ae, config.escalator.tt_escalation_limit
                )
                metrics["escalation_throttled"] += 1
                alarm.set_escalation_error(
                    "Escalation limit exceeded (%s/%s). Skipping" % (
                        ae, config.escalator.tt_escalation_limit))
                return
            # Check whether consequences has escalations
            cons_escalated = sorted(alarm.iter_escalated(),
                                    key=operator.attrgetter("timestamp"))
            affected_objects = sorted(alarm.iter_affected(),
                                      key=operator.attrgetter("name"))
            #
            segment = alarm.managed_object.segment
            if segment.is_redundant:
                uplinks = alarm.managed_object.data.uplinks
                lost_redundancy = len(uplinks) > 1
                affected_subscribers = summary_to_list(
                    segment.total_subscribers,
                    SubscriberProfile
                )
                affected_services = summary_to_list(
                    segment.total_services,
                    ServiceProfile
                )
            else:
                lost_redundancy = False
                affected_subscribers = []
                affected_services = []
            #
            ctx = {
                "alarm": alarm,
                "affected_objects": affected_objects,
                "cons_escalated": cons_escalated,
                "total_objects": summary_to_list(alarm.total_objects, ManagedObjectProfile),
                "total_subscribers": summary_to_list(alarm.total_subscribers, SubscriberProfile),
                "total_services": summary_to_list(alarm.total_services, ServiceProfile),
                "tt": None,
                "lost_redundancy": lost_redundancy,
                "affected_subscribers": affected_subscribers,
                "affected_services": affected_services
            }
            # Escalate to TT
            if a.create_tt and mo.can_escalate():
                tt_id = None
                if alarm.escalation_tt:
                    log(
                        "Already escalated with TT #%s",
                        alarm.escalation_tt
                    )
                else:
                    pre_reason = escalation.get_pre_reason(mo.tt_system)
                    active_maintenance = Maintenance.get_object_maintenance(mo)
                    if active_maintenance:
                        for m in active_maintenance:
                            log("Object is under maintenance: %s (%s-%s)",
                                m.subject, m.start, m.stop)
                        metrics["escalation_stop_on_maintenance"] += 1
                    elif pre_reason is not None:
                        subject = a.template.render_subject(**ctx)
                        body = a.template.render_body(**ctx)
                        logger.debug("[%s] Escalation message:\nSubject: %s\n%s",
                                     alarm_id, subject, body)
                        log("Creating TT in system %s", mo.tt_system.name)
                        tts = mo.tt_system.get_system()
                        try:
                            try:
                                tt_id = tts.create_tt(
                                    queue=mo.tt_queue,
                                    obj=mo.tt_system_id,
                                    reason=pre_reason,
                                    subject=subject,
                                    body=body,
                                    login="correlator",
                                    timestamp=alarm.timestamp
                                )
                            except TemporaryTTError as e:
                                metrics["escalation_tt_retry"] += 1
                                log("Temporary error detected. Retry after %ss", RETRY_TIMEOUT)
                                mo.tt_system.register_failure()
                                Job.retry_after(get_next_retry(), str(e))
                            ctx["tt"] = "%s:%s" % (mo.tt_system.name, tt_id)
                            alarm.escalate(ctx["tt"], close_tt=a.close_tt)
                            if tts.promote_group_tt:
                                # Create group TT
                                log("Promoting to group tt")
                                gtt = tts.create_group_tt(
                                    tt_id,
                                    alarm.timestamp
                                )
                                # Append affected objects
                                for ao in alarm.iter_affected():
                                    if ao.can_escalate(True):
                                        if ao.tt_system == mo.tt_system:
                                            log(
                                                "Appending object %s to group tt %s",
                                                ao.name,
                                                gtt
                                            )
                                            try:
                                                tts.add_to_group_tt(
                                                    gtt,
                                                    ao.tt_system_id
                                                )
                                            except TTError as e:
                                                alarm.set_escalation_error(
                                                    "[%s] %s" % (mo.tt_system.name, e)
                                                )
                                        else:
                                            log(
                                                "Cannot append object %s to group tt %s: Belongs to other TT system",
                                                ao.name,
                                                gtt
                                            )
                                    else:
                                        log(
                                            "Cannot append object %s to group tt %s: Escalations are disabled",
                                            ao.name,
                                            gtt
                                        )
                            metrics["escalation_tt_create"] += 1
                        except TTError as e:
                            log("Failed to create TT: %s", e)
                            metrics["escalation_tt_fail"] += 1
                            alarm.log_message(
                                "Failed to escalate: %s" % e,
                                to_save=True
                            )
                            alarm.set_escalation_error(
                                "[%s] %s" % (mo.tt_system.name, e))
                    else:
                        log("Cannot find pre reason")
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
                            except NotImplementedError:
                                log("Cannot add comment to %s: Feature not implemented", ca.escalation_tt)
                                metrics["escalation_tt_comment_fail"] += 1
                            except TTError as e:
                                log("Failed to add comment to %s: %s",
                                    ca.escalation_tt, e)
                                metrics["escalation_tt_comment_fail"] += 1
                        else:
                            log("Failed to add comment to %s: Invalid TT system",
                                ca.escalation_tt)
                            metrics["escalation_tt_comment_fail"] += 1
            # Send notification
            if a.notification_group and mo.can_notify():
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
        nalarm = get_alarm(alarm_id)
        if nalarm and nalarm.status == "C" and nalarm.escalation_tt:
            log("Alarm has been closed during escalation. Try to deescalate")
            metrics["escalation_closed_while_escalated"] += 1
            if not nalarm.escalation_close_ts and not nalarm.escalation_close_error:
                notify_close(
                    alarm_id=alarm_id,
                    tt_id=nalarm.escalation_tt,
                    subject="Closing",
                    body="Closing",
                    notification_group_id=alarm.clear_notification_group.id if alarm.clear_notification_group else None,
                    close_tt=alarm.close_tt
                )
        logger.info("[%s] Escalations loop end", alarm_id)


def notify_close(alarm_id, tt_id, subject, body, notification_group_id,
                 close_tt=False):
    def log(message, *args):
        msg = message % args
        logger.info("[%s] %s", alarm_id, msg)

    if tt_id:
        alarm = get_alarm(alarm_id)
        alarm.set_escalation_close_ctx()
        if alarm and alarm.status == "C" and (alarm.escalation_close_ts or alarm.escalation_close_error):
            log("Alarm is already deescalated")
            metrics["escalation_already_deescalated"] += 1
            return
        with Span(client="escalator", sample=PARENT_SAMPLE):
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
                        if alarm:
                            alarm.close_escalation()
                    except TemporaryTTError as e:
                        log("Temporary error detected while closing tt %s: %s", tt_id, e)
                        metrics["escalation_tt_close_retry"] += 1
                        Job.retry_after(get_next_retry(), str(e))
                        cts.register_failure()
                        if alarm:
                            alarm.set_escalation_close_error(
                                "[%s] %s" % (alarm.managed_object.tt_system.name, e)
                            )
                    except TTError as e:
                        log("Failed to close tt %s: %s",
                            tt_id, e)
                        metrics["escalation_tt_close_fail"] += 1
                        if alarm:
                            alarm.set_escalation_close_error(
                                "[%s] %s" % (alarm.managed_object.tt_system.name, e)
                            )
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
                    except TTError as e:
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


def get_next_retry():
    """
    Return next retry considering throttling rate
    :return:
    """
    global RETRY_DELTA, RETRY_TIMEOUT, next_retry, retry_lock

    now = datetime.datetime.now()
    retry = now + datetime.timedelta(seconds=RETRY_TIMEOUT)
    with retry_lock:
        if retry < next_retry:
            retry = next_retry
        next_retry = retry + datetime.timedelta(seconds=RETRY_DELTA)
    delta = retry - now
    return delta.seconds + (1 if delta.microseconds else 0)
