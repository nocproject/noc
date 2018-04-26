#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# noc-correlator daemon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import datetime
import re
from collections import defaultdict
from threading import Lock
# Third-party modules
from mongoengine.queryset import Q
# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.core.scheduler.scheduler import Scheduler
from services.correlator.rule import Rule
from services.correlator.rcacondition import RCACondition
from services.correlator.trigger import Trigger
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmlog import AlarmLog
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmtrigger import AlarmTrigger
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.fm.models.alarmdiagnosticconfig import AlarmDiagnosticConfig
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.version import version
from noc.core.debug import format_frames, get_traceback_frames, error_report
from services.correlator import utils
from noc.lib.dateutils import total_seconds


class CorrelatorService(Service):
    name = "correlator"
    pooled = True
    leader_lock_name = "correlator-%(pool)s"
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(CorrelatorService, self).__init__()
        self.version = version.version
        self.rules = {}  # event_class -> [Rule]
        self.back_rules = {}  # event_class -> [Rule]
        self.triggers = {}  # alarm_class -> [Trigger1, .. , TriggerN]
        self.rca_forward = {}  # alarm_class -> [RCA condition, ..., RCA condititon]
        self.rca_reverse = defaultdict(set)  # alarm_class -> set([alarm_class])
        self.scheduler = None
        self.rca_lock = Lock()
        self.topology_rca_lock = Lock()

    def on_activate(self):
        self.scheduler = Scheduler(
            self.name,
            pool=config.pool,
            reset_running=True,
            max_threads=config.correlator.max_threads,
            ioloop=self.ioloop,
            # @fixme have to be configured ?
            submit_threshold=100,
            max_chunk=100
        )
        self.scheduler.correlator = self
        self.subscribe(
            "correlator.dispose.%s" % config.pool,
            "dispose",
            self.on_dispose_event,
            max_in_flight=config.correlator.max_threads
        )
        self.scheduler.run()

    def on_start(self):
        """
        Load rules from database just after loading config
        """
        super(CorrelatorService, self).on_start()
        self.load_rules()
        self.load_triggers()
        self.load_rca_rules()

    def load_rules(self):
        """
        Load rules from database
        """
        self.logger.debug("Loading rules")
        self.rules = {}
        self.back_rules = {}
        nr = 0
        nbr = 0
        for c in EventClass.objects.all():
            if c.disposition:
                r = []
                for dr in c.disposition:
                    rule = Rule(c, dr)
                    r += [rule]
                    nr += 1
                    if dr.combo_condition != "none" and dr.combo_window:
                        for cc in dr.combo_event_classes:
                            try:
                                self.back_rules[cc.id] += [dr]
                            except KeyError:
                                self.back_rules[cc.id] = [dr]
                            nbr += 1
                self.rules[c.id] = r
        self.logger.debug("%d rules are loaded. %d combos" % (nr, nbr))

    def load_triggers(self):
        self.logger.info("Loading triggers")
        self.triggers = {}
        n = 0
        cn = 0
        ec = [(c.name, c.id) for c in AlarmClass.objects.all()]
        for t in AlarmTrigger.objects.filter(is_enabled=True):
            self.logger.debug("Trigger '%s' for classes:" % t.name)
            for c_name, c_id in ec:
                if re.search(t.alarm_class_re, c_name, re.IGNORECASE):
                    try:
                        self.triggers[c_id] += [Trigger(t)]
                    except KeyError:
                        self.triggers[c_id] = [Trigger(t)]
                    cn += 1
                    self.logger.debug("    %s" % c_name)
            n += 1
        self.logger.info("%d triggers has been loaded to %d classes" % (n, cn))

    def load_rca_rules(self):
        """
        Load root cause analisys rules
        """
        self.logger.info("Loading RCA Rules")
        n = 0
        self.rca_forward = {}
        self.rca_reverse = {}
        for a in AlarmClass.objects.filter(root_cause__0__exists=True):
            if not a.root_cause:
                continue
            self.rca_forward[a.id] = []
            for c in a.root_cause:
                rc = RCACondition(a, c)
                self.rca_forward[a.id] += [rc]
                if rc.root.id not in self.rca_reverse:
                    self.rca_reverse[rc.root.id] = []
                self.rca_reverse[rc.root.id] += [rc]
                n += 1
        self.logger.info("%d RCA Rules have been loaded" % n)

    def mark_as_failed(self, event):
        """
        Write error log and mark event as failed
        """
        self.logger.error("Failed to process event %s" % str(event.id))
        # Prepare traceback
        t, v, tb = sys.exc_info()
        now = datetime.datetime.now()
        r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
        r += [str(t), str(v)]
        r += [format_frames(get_traceback_frames(tb))]
        r = "\n".join(r)
        event.mark_as_failed(version=self.version, traceback=r)

    def set_root_cause(self, a):
        """
        Search for root cause and set, if found
        :returns: Boolean. True, if root cause set
        """
        for rc in self.rca_forward[a.alarm_class.id]:
            # Check condition
            if not rc.check_condition(a):
                continue
            # Check match condition
            q = rc.get_match_condition(a)
            root = ActiveAlarm.objects.filter(**q).first()
            if root:
                # Root cause found
                self.logger.info("%s is root cause for %s (Rule: %s)",
                                 root.id, a.id, rc.name)
                self.perf_metrics["alarm_correlated_rule"] += 1
                a.set_root(root)
                return True
        return False

    def set_reverse_root_cause(self, a):
        """
        Set *a* as root cause for existing events
        :param a:
        :return:
        """
        found = False
        for rc in self.rca_reverse[a.alarm_class.id]:
            # Check reverse match condition
            q = rc.get_reverse_match_condition(a)
            for ca in ActiveAlarm.objects.filter(**q):
                # Check condition
                if not rc.check_condition(ca):
                    continue
                # Try to set root cause
                qq = rc.get_match_condition(ca, id=a.id)
                rr = ActiveAlarm.objects.filter(**qq).first()
                if rr:
                    # Reverse root cause found
                    self.logger.info(
                        "%s is root cause for %s (Reverse rule: %s)",
                        a.id, ca.id, rc.name
                    )
                    self.perf_metrics["alarm_correlated_rule"] += 1
                    ca.set_root(a)
                    found = True
        return found

    def raise_alarm(self, r, e):
        managed_object = self.eval_expression(r.managed_object, event=e)
        if not managed_object:
            self.logger.info("Empty managed object, ignoring")
            return
        # @todo: Make configurable
        if not managed_object.is_managed:
            self.logger.info("Managed object is not managed. Do not raise alarm")
            return
        if e.managed_object.id != managed_object.id:
            self.perf_metrics["alarm_change_mo"] += 1
            self.logger.info(
                "Changing managed object to %s",
                managed_object.name
            )
        discriminator, vars = r.get_vars(e)
        if r.unique:
            assert discriminator is not None
            a = ActiveAlarm.objects.filter(
                managed_object=managed_object.id,
                discriminator=discriminator).first()
            if not a:
                # Try to reopen alarm
                a = ArchivedAlarm.objects.filter(
                    managed_object=managed_object.id,
                    discriminator=discriminator,
                    control_time__gte=e.timestamp
                ).first()
                if a:
                    # Reopen alarm
                    self.logger.info(
                        "[%s|%s|%s] %s reopens alarm %s(%s)",
                        e.id, managed_object.name, managed_object.address,
                        e.event_class.name,
                        a.alarm_class.name, a.id
                    )
                    a = a.reopen("Reopened by disposition rule '%s'" % r.u_name)
                    self.perf_metrics["alarm_reopen"] += 1
            if a:
                # Active alarm found, refresh
                self.logger.info(
                    "[%s|%s|%s] Contributing event %s to active alarm %s(%s)",
                    e.id, managed_object.name, managed_object.address,
                    e.event_class.name,
                    a.alarm_class.name, a.id
                )
                # Contribute event to alarm
                e.contribute_to_alarm(a)
                if e.timestamp < a.timestamp:
                    # Set to earlier date
                    a.timestamp = e.timestamp
                    a.save()
                elif e.timestamp > a.last_update:
                    # Refresh last update
                    a.last_update = e.timestamp
                    a.save()
                self.perf_metrics["alarm_contribute"] += 1
                return
        # Calculate alarm coverage
        summary = ServiceSummary.get_object_summary(managed_object)
        summary["object"] = {
            managed_object.object_profile.id: 1
        }
        #
        severity = max(ServiceSummary.get_severity(summary), 1)
        self.logger.info(
            "[%s|%s|%s] %s: Calculated alarm severity is: %s",
            e.id, managed_object.name, managed_object.address,
            r.u_name, severity
        )
        # Create new alarm
        a = ActiveAlarm(
            timestamp=e.timestamp,
            last_update=e.timestamp,
            managed_object=managed_object.id,
            alarm_class=r.alarm_class,
            severity=severity,
            vars=vars,
            discriminator=discriminator,
            direct_services=SummaryItem.dict_to_items(summary["service"]),
            direct_subscribers=SummaryItem.dict_to_items(summary["subscriber"]),
            total_objects=ObjectSummaryItem.dict_to_items(summary["object"]),
            total_services=SummaryItem.dict_to_items(summary["service"]),
            total_subscribers=SummaryItem.dict_to_items(summary["subscriber"]),
            log=[
                AlarmLog(
                    timestamp=datetime.datetime.now(),
                    from_status="A",
                    to_status="A",
                    message="Alarm risen from event %s(%s) by rule '%s'" % (
                        str(e.id), str(e.event_class.name), r.u_name)
                )
            ],
            opening_event=e.id
        )
        a.save()
        e.contribute_to_alarm(a)
        self.logger.info(
            "[%s|%s|%s] %s raises alarm %s(%s): %r",
            e.id, managed_object.name, managed_object.address,
            e.event_class.name,
            a.alarm_class.name, a.id, a.vars
        )
        self.perf_metrics["alarm_raise"] += 1
        self.correlate(r, a)
        # Notify about new alarm
        if not a.root:
            a.managed_object.event(a.managed_object.EV_ALARM_RISEN, {
                "alarm": a,
                "subject": a.subject,
                "body": a.body,
                "symptoms": a.alarm_class.symptoms,
                "recommended_actions": a.alarm_class.recommended_actions,
                "probable_causes": a.alarm_class.probable_causes
            }, delay=a.alarm_class.get_notification_delay())
        # Gather diagnostics when necessary
        AlarmDiagnosticConfig.on_raise(a)
        # Watch for escalations, when necessary
        if config.correlator.auto_escalation and not a.root:
            AlarmEscalation.watch_escalations(a)

    def correlate(self, r, a):
        # Topology RCA
        if a.alarm_class.topology_rca:
            with self.topology_rca_lock:
                self.topology_rca(a)
        # Rule-based RCA
        with self.rca_lock:
            if a.alarm_class.id in self.rca_forward:
                # Check alarm is a consequence of existing one
                self.set_root_cause(a)
            if a.alarm_class.id in self.rca_reverse:
                # Check alarm is the root cause for existing ones
                self.set_reverse_root_cause(a)
        # Call handlers
        for h in a.alarm_class.get_handlers():
            try:
                has_root = bool(a.root)
                h(a)
                if not has_root and a.root:
                    self.logger.info(
                        "[%s|%s|%s] Set root to %s (handler %s)",
                        a.id, a.managed_object.name, a.managed_object.address,
                        a.root, h
                    )
            except:  # noqa. Can probable happens anything from handler
                error_report()
                self.perf_metrics["error", ("type", "alarm_handler")] += 1
        # Call triggers if necessary
        if r.alarm_class.id in self.triggers:
            for t in self.triggers[r.alarm_class.id]:
                try:
                    t.call(a)
                except: # noqa. Can probable happens anything from trigger
                    error_report()
        #
        if not a.severity:
            # Alarm severity has been reset to 0 by handlers
            # Silently drop alarm
            self.logger.debug("Alarm severity is 0, dropping")
            a.delete()
            self.perf_metrics["alarm_drop"] += 1
            return

    def clear_alarm(self, r, e):
        managed_object = self.eval_expression(r.managed_object, event=e)
        if not managed_object:
            self.logger.info(
                "[%s|Unknown|Unknown] Referred to unknown managed object, ignoring",
                e.id
            )
            self.perf_metrics["unknown_object"] += 1
            return
        if r.unique:
            discriminator, vars = r.get_vars(e)
            assert discriminator is not None
            a = ActiveAlarm.objects.filter(
                managed_object=managed_object.id,
                discriminator=discriminator).first()
            if a:
                self.logger.info(
                    "[%s|%s|%s] %s clears alarm %s(%s)",
                    e.id, managed_object.name, managed_object.address,
                    e.event_class.name,
                    a.alarm_class.name, a.id
                )
                e.contribute_to_alarm(a)
                a.closing_event = e.id
                a.last_update = max(a.last_update, e.timestamp)
                a.clear_alarm(
                    "Cleared by disposition rule '%s'" % r.u_name,
                    ts=e.timestamp
                )
                self.perf_metrics["alarm_clear"] += 1

    def get_delayed_event(self, r, e):
        """
        Check wrether all delayed conditions are met

        :param r: Delayed rule
        :param e: Event which can trigger delayed rule
        """
        # @todo: Rewrite to scheduler
        discriminator, vars = r.get_vars(e)
        ws = e.timestamp - datetime.timedelta(seconds=r.combo_window)
        de = ActiveEvent.objects.filter(
            managed_object=e.managed_object_id,
            event_class=r.event_class,
            discriminator=discriminator,
            timestamp__gte=ws
        ).first()
        if not de:
            # No starting event
            return None
        # Probable starting event found, get all interesting following event
        # classes
        fe = [
            ee.event_class.id
            for ee in ActiveEvent.objects.filter(
                managed_object=e.managed_object_id,
                event_class__in=r.combo_event_classes,
                discriminator=discriminator,
                timestamp__gte=ws
            ).order_by("timestamp")
        ]
        if r.combo_condition == "sequence":
            # Exact match
            if fe == self.combo_event_classes:
                return de
        elif r.combo_condition == "all":
            # All present
            if not any([c for c in r.combo_event_classes if c not in fe]):
                return de
        elif r.combo_condition == "any":
            # Any found
            if fe:
                return de
        return None

    def eval_expression(self, expression, **kwargs):
        """
        Evaluate expression in given context
        """
        env = {
            "re": re,
            "utils": utils
        }
        env.update(kwargs)
        return eval(expression, {}, env)

    def on_dispose_event(self, message, event_id, event=None, *args, **kwargs):
        """
        Called on new dispose message
        """
        self.logger.info("[%s] Receiving message", event_id)
        message.enable_async()
        self.get_executor("max").submit(self.dispose_worker, message, event_id, event)

    def dispose_worker(self, message, event_id, event_hint=None):
        self.perf_metrics["alarm_dispose"] += 1
        try:
            if event_hint:
                event = self.get_event_from_hint(event_hint)
            else:
                event = self.lookup_event(event_id)
            if event:
                self.dispose_event(event)
        except Exception:
            self.perf_metrics["alarm_dispose_error"] += 1
            error_report()
        self.ioloop.add_callback(message.finish)

    def lookup_event(self, event_id):
        """
        Lookup event by id.
        Uses cache heating effect from classifier
        :param event_id:
        :return: ActiveEvent instance or None
        """
        self.logger.info("[%s] Lookup event", event_id)
        e = ActiveEvent.get_by_id(event_id)
        if not e:
            self.logger.info("[%s] Event not found, skipping", event_id)
            self.perf_metrics["event_lookup_failed"] += 1
        self.perf_metrics["event_lookups"] += 1
        return e

    def get_event_from_hint(self, hint):
        """
        Get ActiveEvent from json hint
        :param hint:
        :return:
        """
        self.perf_metrics["event_hints"] += 1
        e = ActiveEvent.from_json(hint)
        # Prevent TypeError: can't compare offset-naive and offset-aware datetimes
        # when calculating alarm timestamp
        e.timestamp = e.timestamp.replace(tzinfo=None)
        return e

    def dispose_event(self, e):
        """
        Dispose event according to disposition rule
        """
        event_id = str(e.id)
        self.logger.info("[%s] Disposing", event_id)
        drc = self.rules.get(e.event_class.id)
        if not drc:
            self.logger.info("[%s] No disposition rules for class %s, skipping",
                             event_id, e.event_class.name)
            return
        # Apply disposition rules
        for r in drc:
            if self.eval_expression(r.condition, event=e):
                # Process action
                if r.action == "drop":
                    self.logger.info("[%s] Dropped by action", event_id)
                    e.delete()
                    return
                elif r.action == "ignore":
                    self.logger.info("[%s] Ignored by action", event_id)
                    return
                elif r.action == "raise" and r.combo_condition == "none":
                    self.raise_alarm(r, e)
                elif r.action == "clear" and r.combo_condition == "none":
                    self.clear_alarm(r, e)
                if r.action in ("raise", "clear"):
                    # Write discriminator if can trigger delayed event
                    if r.unique and r.event_class.id in self.back_rules:
                        discriminator, vars = r.get_vars(e)
                        e.discriminator = discriminator
                        e.save()
                    # Process delayed combo conditions
                    if e.event_class.id in self.back_rules:
                        for br in self.back_rules[e.event_class.id]:
                            de = self.get_delayed_event(br, e)
                            if de:
                                if br.action == "raise":
                                    self.raise_alarm(br, de)
                                elif br.action == "clear":
                                    self.clear_alarm(br, de)
                if r.stop_disposition:
                    break
        self.logger.info("[%s] Disposition complete", event_id)

    def topology_rca(self, alarm, seen=None):
        def can_correlate(a1, a2):
            return (
                not config.correlator.topology_rca_window or
                total_seconds(a1.timestamp - a2.timestamp) <= config.correlator.topology_rca_window
            )

        self.logger.debug("[%s] Topology RCA", alarm.id)
        seen = seen or set()
        if alarm.root or alarm.id in seen:
            self.logger.debug("[%s] Already correlated", alarm.id)
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
            self.logger.info("[%s] All uplinks are faulty. Correlating", alarm.id)
            for u in alarm.uplinks:
                a = na[u]
                if can_correlate(alarm, a):
                    self.logger.info("[%s] Set root to %s", alarm.id, a.id)
                    alarm.set_root(a)
                    self.perf_metrics["alarm_correlated_topology"] += 1
                    break
        # Correlate neighbors' alarms
        for d in na:
            self.topology_rca(na[d], seen)
        self.logger.debug("[%s] Correlation completed", alarm.id)


if __name__ == "__main__":
    CorrelatorService().start()
