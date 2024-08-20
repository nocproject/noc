#!./bin/python
# ---------------------------------------------------------------------
# noc-correlator daemon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import datetime
import re
from collections import defaultdict, deque
import threading
from typing import DefaultDict, Union, Any, Iterable, Optional, Tuple, Dict, List, Set
import operator
from itertools import chain
from hashlib import sha512
import asyncio

# Third-party modules
import orjson
from bson import ObjectId
from dateutil.parser import parse as parse_date
from pydantic import TypeAdapter, ValidationError
import cachetools
from pymongo import UpdateOne

# NOC modules
from noc.config import config
from noc.core.scheduler.scheduler import Scheduler
from noc.core.service.fastapi import FastAPIService
from noc.core.mongo.connection import connect
from noc.core.change.policy import change_tracker
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.service import Service, SVC_REF_PREFIX
from noc.services.correlator.alarmrule import AlarmRuleSet, AlarmRule as CAlarmRule
from noc.services.correlator.rule import Rule
from noc.services.correlator.rcacondition import RCACondition
from noc.services.correlator.trigger import Trigger
from noc.services.correlator.models.disposereq import DisposeRequest
from noc.services.correlator.models.eventreq import EventRequest
from noc.services.correlator.models.clearreq import ClearRequest
from noc.services.correlator.models.clearidreq import ClearIdRequest
from noc.services.correlator.models.raisereq import RaiseRequest
from noc.services.correlator.models.ensuregroupreq import EnsureGroupRequest
from noc.services.correlator.models.setstatusreq import SetStatusRequest
from noc.fm.models.eventclass import EventClass
from noc.fm.models.activealarm import ActiveAlarm, ComponentHub
from noc.fm.models.alarmlog import AlarmLog
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmtrigger import AlarmTrigger
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.escalation import Escalation, ItemStatus
from noc.fm.models.alarmdiagnosticconfig import AlarmDiagnosticConfig
from noc.fm.models.alarmrule import AlarmRule
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.inv.models.channel import Channel
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.version import version
from noc.core.debug import format_frames, get_traceback_frames, error_report
from noc.services.correlator import utils
from noc.core.defer import defer
from noc.core.perf import metrics
from noc.core.fm.enum import RCA_RULE, RCA_TOPOLOGY, RCA_DOWNLINK_MERGE
from noc.core.msgstream.message import Message
from noc.core.wf.interaction import Interaction
from noc.core.fm.event import Event
from noc.services.correlator.rcalock import RCALock
from noc.services.correlator.alarmrule import GroupItem

ref_lock = threading.Lock()
ta_DisposeRequest = TypeAdapter(DisposeRequest)


class CorrelatorService(FastAPIService):
    name = "correlator"
    pooled = True
    use_mongo = True
    process_name = "noc-%(name).10s-%(pool).5s"

    _reference_cache = cachetools.TTLCache(100, ttl=60)
    AVAIL_CLS = "NOC | Managed Object | Ping Failed"

    def __init__(self):
        super().__init__()
        self.version = version.version
        self.rules: Dict[ObjectId, List[Rule]] = {}
        self.back_rules: Dict[ObjectId, List[Rule]] = {}
        self.triggers: Dict[ObjectId, List[Trigger]] = {}
        self.rca_forward = {}  # alarm_class -> [RCA condition, ..., RCA condititon]
        self.rca_reverse = defaultdict(set)  # alarm_class -> set([alarm_class])
        self.alarm_rule_set = AlarmRuleSet()
        self.alarm_class_vars = defaultdict(dict)
        self.status_changes = deque([])  # Save status changes
        #
        self.slot_number = 0
        self.total_slots = 0
        self.is_distributed = False
        # Scheduler
        self.scheduler: Optional[Scheduler] = None
        # Locks
        self.topo_rca_lock: Optional[RCALock] = None

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        self.is_distributed = self.total_slots > 1
        # Prepare scheduler
        if self.is_distributed:
            self.logger.info(
                "Enabling distributed mode: Slot %d/%d", self.slot_number, self.total_slots
            )
            ifilter = {"shard": {"$mod": [self.total_slots, self.slot_number]}}
        else:
            self.logger.info("Enabling standalone mode")
            ifilter = None
        self.scheduler = Scheduler(
            self.name,
            pool=config.pool,
            reset_running=True,
            max_threads=config.correlator.max_threads,
            # @fixme have to be configured ?
            submit_threshold=100,
            max_chunk=100,
            filter=ifilter,
        )
        self.scheduler.correlator = self
        self.scheduler.run()
        asyncio.create_task(self.update_object_statuses())
        # Subscribe stream, move to separate task to let the on_activate to terminate
        self.loop.create_task(
            self.subscribe_stream(
                "dispose.%s" % config.pool,
                self.slot_number,
                self.on_dispose_event,
                async_cursor=config.correlator.allowed_async_cursor,
            )
        )

    def on_start(self):
        """
        Load rules from database just after loading config
        """
        super().on_start()
        connect()  # use_mongo connect do after on_start.
        self.load_rules()
        self.load_triggers()
        self.load_rca_rules()
        self.load_alarm_rules()
        self.load_vars()

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
        self.logger.debug("%d rules are loaded. %d combos", nr, nbr)

    def load_vars(self):
        self.logger.info("Loading AlarmClass vars")
        for alarm_class in AlarmClass.objects.all():
            # Default variables
            for v in alarm_class.vars:
                if v.default:
                    if v.default.startswith("="):
                        # Expression
                        # Check component '=component.<name>'
                        _, c_name, *_ = v.default[1:].split(".", 2)
                        self.alarm_class_vars[alarm_class.id][v.name] = compile(
                            f'{v.default[1:]} if "{c_name}" in components else None',
                            "<string>",
                            "eval",
                        )
                    else:
                        # Constant
                        self.alarm_class_vars[alarm_class.id][v.name] = v.default

    def load_triggers(self):
        self.logger.info("Loading triggers")
        self.triggers = {}
        n = 0
        cn = 0
        ec = [(c.name, c.id) for c in AlarmClass.objects.all()]
        for t in AlarmTrigger.objects.filter(is_enabled=True):
            self.logger.debug("Trigger '%s' for classes:", t.name)
            for c_name, c_id in ec:
                if re.search(t.alarm_class_re, c_name, re.IGNORECASE):
                    try:
                        self.triggers[c_id] += [Trigger(t)]
                    except KeyError:
                        self.triggers[c_id] = [Trigger(t)]
                    cn += 1
                    self.logger.debug("    %s", c_name)
            n += 1
        self.logger.info("%d triggers has been loaded to %d classes", n, cn)

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
        self.logger.info("%d RCA Rules have been loaded", n)

    def load_alarm_rules(self):
        """
        Load Alarm Rules
        """
        self.logger.info("Loading alarm rules")
        n = 0
        for rule in AlarmRule.objects.filter(is_active=True):
            self.alarm_rule_set.add(rule)
            n += 1
        self.alarm_rule_set.compile()
        self.logger.info("%d Alam Rules have been loaded", n)

    def mark_as_failed(self, event: "Event"):
        """
        Write error log and mark event as failed
        """
        self.logger.error("Failed to process event %s", event.id)
        # Prepare traceback
        t, v, tb = sys.exc_info()
        now = datetime.datetime.now()
        r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
        r += [str(t), str(v)]
        r += [format_frames(get_traceback_frames(tb))]
        r = "\n".join(r)
        event.mark_as_failed(version=self.version, traceback=r)

    def set_root_cause(self, a: ActiveAlarm) -> bool:
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
                self.logger.info("%s is root cause for %s (Rule: %s)", root.id, a.id, rc.name)
                metrics["alarm_correlated_rule"] += 1
                a.set_root(root, rca_type=RCA_RULE)
                return True
        return False

    def set_reverse_root_cause(self, a: ActiveAlarm) -> bool:
        """
        Set `a` as root cause for existing events
        :param a:
        :return: True, if set as root
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
                        "%s is root cause for %s (Reverse rule: %s)", a.id, ca.id, rc.name
                    )
                    metrics["alarm_correlated_rule"] += 1
                    ca.set_root(a, rca_type=RCA_RULE)
                    found = True
        return found

    @staticmethod
    def get_default_reference(
        managed_object: ManagedObject, alarm_class: AlarmClass, vars: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate default reference for event-based alarms.
        Reference has a form of

        ```
        e:<mo id>:<alarm class id>:<value1>:...:<value N>
        ```

        :param managed_object: Managed Object instance
        :param alarm_class: Alarm Class instance
        :param vars: Variables
        :returns: Reference string
        """
        if not vars:
            return f"e:{managed_object.id}:{alarm_class.id}"
        var_suffix = ":".join(
            str(vars.get(n, "")).replace("\\", "\\\\").replace(":", r"\:")
            for n in alarm_class.reference
        )
        return f"e:{managed_object.id}:{alarm_class.id}:{var_suffix}"

    @staticmethod
    def get_reference_hash(reference: str) -> bytes:
        """
        Generate hashed form of reference
        """
        return sha512(reference.encode("utf-8")).digest()[:10]

    def try_reopen_alarm(
        self,
        reference: bytes,
        timestamp: datetime.datetime,
        event: Event = None,
    ) -> Optional[ActiveAlarm]:
        """
        Try to reopen archived alarm

        :param reference: Reference hash
        :param timestamp: New alarm timestamp
        :param event:
        :returns: Reopened alarm, when found, None otherwise
        """
        arch = ArchivedAlarm.objects.filter(
            reference=reference,
            control_time__gte=timestamp,
        ).first()
        if not arch:
            return None
        if event:
            self.logger.info(
                "[%s|%s|%s] %s reopens alarm %s(%s)",
                event.id,
                arch.managed_object.name,
                arch.managed_object.address,
                event.type.event_class,
                arch.alarm_class.name,
                arch.id,
            )
            reason = f"Reopened by {event.type.event_class}({event.id})"
        else:
            reason = "Reopened by alarm"
        alarm = arch.reopen(reason)
        metrics["alarm_reopen"] += 1
        return alarm

    def refresh_alarm(
        self,
        alarm: ActiveAlarm,
        timestamp: datetime.datetime,
        severity: Optional[AlarmSeverity] = None,
    ):
        """
        Refresh active alarm data
        """
        self.logger.info("[%s] Refresh alarm: ts: %s, severity: %s", alarm.id, timestamp, severity)
        if timestamp < alarm.timestamp:
            # Set to earlier date
            alarm.timestamp = timestamp
            alarm.save()
        elif timestamp > alarm.last_update:
            # Refresh last update
            alarm.last_update = timestamp
            alarm.save()
        if not severity:
            return
        e_severity = alarm.get_effective_severity(severity=severity)
        if e_severity != alarm.severity:
            alarm.base_severity = severity.severity
            alarm.severity = e_severity
            alarm.last_update = datetime.datetime.now().replace(microsecond=0)
            alarm.save()

    async def raise_alarm(
        self,
        managed_object: ManagedObject,
        timestamp: datetime.datetime,
        alarm_class: AlarmClass,
        vars: Optional[Dict[str, Any]],
        event: Optional[Event] = None,
        reference: Optional[str] = None,
        remote_system: Optional[RemoteSystem] = None,
        remote_id: Optional[str] = None,
        groups: Optional[List[GroupItem]] = None,
        labels: Optional[List[str]] = None,
        min_group_size: Optional[int] = None,
        severity: Optional[AlarmSeverity] = None,
    ) -> Optional[ActiveAlarm]:
        """
        Raise alarm
        :param managed_object: Managed Object instance
        :param timestamp: Alarm Timestamp
        :param alarm_class: Alarm Class reference
        :param vars: Alarm variables
        :param event:
        :param reference:
        :param remote_system:
        :param remote_id:
        :param groups:
        :param labels:
        :param min_group_size: For Group alarm, minimal count alarm on it
        :param severity: Alarm Severity source
        :returns: Alarm, if created, None otherwise
        """

        scope_label = str(event.id) if event else "DIRECT"
        labels = labels or []
        # @todo: Make configurable
        if Interaction.Alarm not in managed_object.interactions:
            self.logger.info("Managed object is allowed processed Alarm. Do not raise alarm")
            return None
        if not reference:
            reference = self.get_default_reference(
                managed_object=managed_object, alarm_class=alarm_class, vars=vars
            )
        ref_hash = self.get_reference_hash(reference)
        if alarm_class.is_unique:
            alarm = ActiveAlarm.objects.filter(reference=ref_hash).first()
            if not alarm:
                alarm = self.try_reopen_alarm(
                    reference=ref_hash,
                    timestamp=timestamp,
                    event=event,
                )
            if alarm:
                self.logger.info(
                    "[%s|%s|%s] Contributing %s to active alarm %s(%s)",
                    scope_label,
                    managed_object.name,
                    managed_object.address,
                    f"event {event.type.event_class}" if event else "DIRECT",
                    alarm.alarm_class.name,
                    alarm.id,
                )
                if event:
                    # event.contribute_to_alarm(alarm)  # Add Dispose Log
                    metrics["alarm_contribute"] += 1
                a_severity, e_profile = None, None
                for rule in self.alarm_rule_set.iter_rules(alarm):
                    for aa in rule.iter_actions(alarm):
                        if aa.severity:
                            a_severity = aa.severity
                        if aa.escalation_profile:
                            e_profile = aa.escalation_profile
                self.refresh_alarm(alarm, timestamp, a_severity or severity)
                if alarm.escalation_profile:
                    # Repeat Escalation
                    Escalation.register_item_changes(
                        str(alarm.id),
                        [ItemStatus.REMOVED],
                        ItemStatus.CHANGED,
                    )
                elif config.correlator.auto_escalation and e_profile:
                    Escalation.register_escalation(alarm, e_profile)
                return alarm
        if event:
            msg = f"Alarm risen from event {event.id}({event.type.event_class})"
        else:
            msg = "Alarm risen directly"
        # Create new alarm
        a = ActiveAlarm(
            timestamp=timestamp,
            last_update=timestamp,
            managed_object=managed_object.id,
            alarm_class=alarm_class,
            vars=vars,
            reference=ref_hash,
            log=[
                AlarmLog(
                    timestamp=datetime.datetime.now(),
                    from_status="A",
                    to_status="A",
                    message=msg,
                )
            ],
            opening_event=ObjectId(event.id) if event else None,
            labels=labels,
            min_group_size=min_group_size,
            base_severity=severity.severity if severity else None,
            remote_system=remote_system,
            remote_id=remote_id,
        )
        a.effective_labels = list(chain.from_iterable(ActiveAlarm.iter_effective_labels(a)))
        a.raw_reference = reference
        # Calculate alarm coverage
        if a.alarm_class.affected_service:
            summary = ServiceSummary.get_object_summary(managed_object)
        else:
            summary = {"service": {}, "subscriber": {}, "interface": {}}
        summary["object"] = {managed_object.object_profile.id: 1}
        if a.is_link_alarm and a.components.interface:
            summary["interface"] = {a.components.interface.profile.id: 1}
        # Set alarm stat fields
        a.direct_objects = [ObjectSummaryItem(profile=managed_object.object_profile.id, summary=1)]
        a.direct_services = SummaryItem.dict_to_items(summary["service"])
        a.direct_subscribers = SummaryItem.dict_to_items(summary["subscriber"])
        a.total_objects = ObjectSummaryItem.dict_to_items(summary["object"])
        a.total_services = a.direct_services
        a.total_subscribers = a.direct_subscribers
        a.affected_services = Service.get_services_by_alarm(a)
        a.affected_channels = Channel.get_channels_by_alarm(a)
        # Static groups
        alarm_groups: Dict[str, GroupItem] = {}
        if groups:
            for gi in groups:
                if gi.reference and gi.reference not in alarm_groups:
                    alarm_groups[gi.reference] = gi
        # Apply rules
        escalation_profile = None
        a_severity: Optional[int] = None
        for rule in self.alarm_rule_set.iter_rules(a):
            for gi in rule.iter_groups(a):
                if gi.reference and gi.reference not in alarm_groups:
                    alarm_groups[gi.reference] = gi
            for ai in rule.iter_actions(a):
                if ai.severity:
                    a_severity = a.severity
                if ai.escalation_profile:
                    escalation_profile = ai.escalation_profile
            if a.severity_policy != rule.severity_policy:
                a.severity_policy = rule.severity_policy
        all_groups, deferred_groups = await self.get_groups(a, alarm_groups.values())
        a.groups = [g.reference for g in all_groups]
        a.deferred_groups = deferred_groups
        # Calculate Alarm Severities
        if a_severity:
            a.severity = a_severity
        else:
            # If changed policy
            a.severity = a.get_effective_severity(summary)
        # @todo: Fix
        self.logger.info(
            "[%s|%s|%s] Calculated alarm severity is: %s",
            scope_label,
            managed_object.name,
            managed_object.address,
            a.severity,
        )
        # Save
        a.save()
        # Update group if Service Group Alarm
        if reference.startswith(SVC_REF_PREFIX):
            self.resolve_deferred_groups(a.reference)
        # if event:
        #     event.contribute_to_alarm(a)
        self.logger.info(
            "[%s|%s|%s] Raise alarm %s(%s): %r [%s]",
            scope_label,
            managed_object.name,
            managed_object.address,
            a.alarm_class.name,
            a.id,
            a.vars,
            ", ".join(labels),
        )
        metrics["alarm_raise"] += 1
        await self.correlate(a)
        # Notify about new alarm
        # if not a.root:
        #     a.managed_object.event(
        #         a.managed_object.EV_ALARM_RISEN,
        #         {
        #             "alarm": a,
        #             "subject": a.subject,
        #             "body": a.body,
        #             "symptoms": a.alarm_class.symptoms,
        #             "recommended_actions": a.alarm_class.recommended_actions,
        #             "probable_causes": a.alarm_class.probable_causes,
        #         },
        #         delay=a.alarm_class.get_notification_delay(),
        #     )
        # Gather diagnostics when necessary
        AlarmDiagnosticConfig.on_raise(a)
        # Update groups summary
        await self.update_groups_summary(a.groups)
        # Watch for escalations, when necessary
        if config.correlator.auto_escalation and not a.root and escalation_profile:
            Escalation.register_escalation(a, escalation_profile)
        elif a.root:
            Escalation.register_item_changes(a.root)
        if a.affected_services:
            defer(
                "noc.sa.models.service.refresh_service_status",
                svc_ids=[str(x) for x in a.affected_services],
            )
        return a

    async def raise_alarm_from_rule(
        self, rule: Rule, event: Event, managed_object
    ) -> Optional[ActiveAlarm]:
        """
        Raise alarm from incoming event
        """
        # Find effective managed object
        managed_object = self.eval_expression(
            rule.managed_object, event=event, managed_object=managed_object
        )
        if not managed_object:
            self.logger.info("Empty managed object, ignoring")
            return
        if int(event.target.id) != managed_object.id:
            metrics["alarm_change_mo"] += 1
            self.logger.info("Changing managed object to %s", managed_object.name)
        if event.type.severity:
            severity = AlarmSeverity.get_by_code(event.type.severity.name)
            self.logger.info("Try request severity %s -> %s", event.type.severity, severity)
        else:
            severity = None
        if event.remote_system:
            rs = RemoteSystem.get_by_name(event.remote_system)
        else:
            rs = None
        # Extract variables
        vars = rule.get_vars(event, managed_object)
        return await self.raise_alarm(
            managed_object=managed_object,
            timestamp=event.timestamp,
            alarm_class=rule.alarm_class,
            vars=vars,
            event=event,
            severity=severity,
            remote_system=rs,
            remote_id=event.remote_id,
        )

    async def channel_rca(self, alarm: ActiveAlarm):
        if alarm.root:
            return
        if alarm.affected_channels:
            for aa in Channel.get_alarms_by_channel(
                alarm.affected_channels,
                alarm_class="NOC | Managed Object | Ping Failed",
            ):
                aa.set_root(alarm)
            return
        channels = Channel.get_channel_by_object(alarm.managed_object)
        if not channels:
            return
        aa = ActiveAlarm.objects.filter(root__exists=False, affected_channels__in=channels).first()
        alarm.set_root(aa)

    async def correlate(self, a: ActiveAlarm):
        # Topology RCA
        if a.alarm_class.topology_rca:
            await self.topology_rca(a)
            await self.channel_rca(a)
        # Rule-based RCA
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
                        a.id,
                        a.managed_object.name,
                        a.managed_object.address,
                        a.root,
                        h,
                    )
            except Exception:  # noqa. Can probable happens anything from handler
                error_report()
                metrics["error", ("type", "alarm_handler")] += 1
        # Call triggers if necessary
        if a.alarm_class.id in self.triggers:
            for t in self.triggers[a.alarm_class.id]:
                try:
                    t.call(a)
                except:  # noqa. Can probable happens anything from trigger
                    error_report()
        #
        if not a.severity:
            # Alarm severity has been reset to 0 by handlers
            # Silently drop alarm
            self.logger.debug("Alarm severity is 0, dropping")
            a.delete()
            metrics["alarm_drop"] += 1
            return

    async def clear_alarm_from_rule(
        self,
        rule: "Rule",
        event: "Event",
        managed_object: ManagedObject,
    ) -> Optional["ActiveAlarm"]:
        managed_object = self.eval_expression(
            rule.managed_object, event=event, managed_object=managed_object
        )
        if not managed_object:
            self.logger.info(
                "[%s|Unknown|Unknown] Referred to unknown managed object, ignoring", event.id
            )
            metrics["unknown_object"] += 1
            return
        if not rule.unique:
            return
        vars = rule.get_vars(event, managed_object)
        reference = self.get_default_reference(
            managed_object=managed_object, alarm_class=rule.alarm_class, vars=vars
        )
        ref_hash = self.get_reference_hash(reference)
        alarm = ActiveAlarm.objects.filter(reference=ref_hash).first()
        if not alarm:
            return
        self.logger.info(
            "[%s|%s|%s] %s clears alarm %s(%s)",
            event.id,
            managed_object.name,
            managed_object.address,
            event.type.event_class,
            alarm.alarm_class.name,
            alarm.id,
        )
        # event.contribute_to_alarm(alarm)
        alarm.closing_event = ObjectId(event.id)
        alarm.last_update = max(alarm.last_update, event.timestamp)
        groups = alarm.groups
        alarm.clear_alarm("Cleared by disposition rule '%s'" % rule.u_name, ts=event.timestamp)
        metrics["alarm_clear"] += 1
        await self.clear_groups(groups, ts=event.timestamp)
        return alarm

    def get_delayed_event(self, rule: Rule, event: Event, managed_object: ManagedObject):
        """
        Check werever all delayed conditions are met

        :param rule: Delayed rule
        :param event: Event which can trigger delayed rule
        :param managed_object: Managed Object on event
        """
        # @todo: Rewrite to scheduler
        vars = rule.get_vars(event, managed_object)
        reference = self.get_default_reference(
            managed_object=managed_object, alarm_class=rule.alarm_class, vars=vars
        )
        ref_hash = self.get_reference_hash(reference)
        ws = event.timestamp - datetime.timedelta(seconds=rule.combo_window)
        de = Event.objects.filter(
            managed_object=event.managed_object_id,
            event_class=rule.event_class,
            reference=ref_hash,
            timestamp__gte=ws,
        ).first()
        if not de:
            # No starting event
            return None
        # Probable starting event found, get all interesting following event classes
        fe = [
            ee.event_class.id
            for ee in Event.objects.filter(
                managed_object=event.managed_object_id,
                event_class__in=rule.combo_event_classes,
                reference=ref_hash,
                timestamp__gte=ws,
            ).order_by("timestamp")
        ]
        if rule.combo_condition == "sequence":
            # Exact match
            if fe == rule.combo_event_classes:
                return de
        elif rule.combo_condition == "all":
            # All present
            if not any([c for c in rule.combo_event_classes if c not in fe]):
                return de
        elif rule.combo_condition == "any":
            # Any found
            if fe:
                return de
        return None

    def eval_expression(self, expression, **kwargs):
        """
        Evaluate expression in given context
        """
        env = {"re": re, "utils": utils}
        env.update(kwargs)
        return eval(expression, {}, env)

    async def on_dispose_event(self, msg: Message) -> None:
        """
        Called on new `dispose` message
        """
        data: Dict[str, Any] = orjson.loads(msg.value)
        # Backward-compatibility
        if "$op" not in data:
            data["$op"] = "event"
        # Parse request
        try:
            req = ta_DisposeRequest.validate_python(data)
        except ValidationError as e:
            self.logger.error("Malformed message: %s", e)
            metrics["malformed_messages"] += 1
            return
        # Call handler, may not be invalid
        msg_handler = getattr(self, f"on_msg_{req.op}")
        if not msg_handler:
            self.logger.error("Internal error. No handler for '%s'", req.op)
            return
        with change_tracker.bulk_changes():
            await msg_handler(req)
            metrics["alarm_dispose"] += 1

    async def on_msg_event(self, req: EventRequest) -> None:
        """
        Process `event` message type
        """
        self.logger.info("[event|%s] Receiving message", req.event_id)
        try:
            event = req.event
            event.ts = event.timestamp.replace(tzinfo=None).timestamp()
            await self.dispose_event(event)
        except Exception:
            metrics["alarm_dispose_error"] += 1
            error_report()
        finally:
            if self.topo_rca_lock:
                # Release pending RCA Lock
                await self.topo_rca_lock.release()
                self.topo_rca_lock = None

    async def on_msg_raise(self, req: RaiseRequest) -> None:
        """
        Process `raise` message.
        """
        # Fetch timestamp
        ts = self.parse_timestamp(req.timestamp)
        # Managed Object
        managed_object = self.parse_object(req.managed_object)
        if not managed_object:
            return
        # Get alarm class
        alarm_class = AlarmClass.get_by_name(req.alarm_class)
        if not alarm_class:
            self.logger.error("Invalid alarm class: %s", req.alarm_class)
            return
        # Groups
        if req.groups:
            groups = []
            for gi in req.groups:
                ac = AlarmClass.get_by_name(gi.alarm_class) if gi.alarm_class else None
                ac = ac or CAlarmRule.get_default_alarm_class()
                gi_name = gi.name or "Alarm Group"
                groups.append(GroupItem(reference=gi.reference, alarm_class=ac, title=gi_name))
        else:
            groups = None
        # Remote system
        if req.remote_system and req.remote_id:
            remote_system = RemoteSystem.get_by_id(req.remote_system)
        else:
            remote_system = None
        r_vars = req.vars or {}
        if req.labels:
            r_vars.update(alarm_class.convert_labels_var(req.labels))
        if alarm_class.id in self.alarm_class_vars:
            # Calculate dynamic defaults
            context = {"components": ComponentHub(alarm_class, managed_object, r_vars.copy())}
            for k, v in self.alarm_class_vars[alarm_class.id].items():
                x = eval(v, {}, context)
                if x:
                    r_vars[k] = str(x)
        if req.severity:
            severity = AlarmSeverity.get_severity(req.severity)
        else:
            severity = None
        try:
            await self.raise_alarm(
                managed_object=managed_object,
                timestamp=ts,
                alarm_class=alarm_class,
                vars=r_vars,
                reference=req.reference,
                groups=groups,
                labels=req.labels or [],
                severity=severity,
                remote_system=remote_system,
                remote_id=req.remote_id if remote_system else None,
            )
        except Exception:
            metrics["alarm_dispose_error"] += 1
            error_report()
        finally:
            if self.topo_rca_lock:
                # Release pending RCA Lock
                await self.topo_rca_lock.release()
                self.topo_rca_lock = None

    def parse_timestamp(self, iso_timestamp: str) -> datetime.datetime:
        """
        It takes a string ISO timestamp, converts it to a datetime object, then converts it to local timezone,
        then removes the timezone info, then returns the datetime object

        :param iso_timestamp: The timestamp of the alarm in ISO format
        :return: A datetime object
        """
        if iso_timestamp:
            timestamp = parse_date(iso_timestamp)
            if timestamp.tzinfo:
                timestamp = timestamp.astimezone(tz=None).replace(tzinfo=None)
            self.logger.debug("Raw timestamp: %s NOC timestamp: %s", iso_timestamp, timestamp)
            return timestamp
        self.logger.debug("Using current time as alarm timestamp")
        return datetime.datetime.now()

    def parse_object(self, oid) -> Optional[ManagedObject]:
        """
        Resolve ManagedObject instance from message id
        :param oid:
        :return:
        """
        if oid.startswith("bi_id:"):
            managed_object = ManagedObject.get_by_bi_id(int(oid[6:]))
        else:
            managed_object = ManagedObject.get_by_id(int(oid))
        if not managed_object:
            self.logger.error("Invalid managed object: %s", oid)
            return
        return managed_object

    async def on_msg_clear(self, req: ClearRequest) -> None:
        """
        Process `clear` message.
        """
        # Fetch timestamp
        ts = self.parse_timestamp(req.timestamp)
        await self.clear_by_reference(req.reference, ts)

    async def on_msg_clearid(self, req: ClearIdRequest) -> None:
        """
        Process `clearid` message.
        """
        # Fetch timestamp
        ts = self.parse_timestamp(req.timestamp)
        await self.clear_by_id(req.id, ts=ts, message=req.message, source=req.source)

    async def on_msg_ensure_group(self, req: EnsureGroupRequest) -> None:
        """
        Process `ensure_group` message.
        """
        # Find existing group alarm
        group_alarm = self.get_by_reference(req.reference)
        if not group_alarm and not req.alarms:
            return  # Nothing to clear, nothing to create
        # Check managed objects and timestamps
        mos: Dict[str, ManagedObject] = {}
        tses: Dict[str, datetime.datetime] = {}
        alarm_classes: Dict[str, AlarmClass] = {}
        for ai in req.alarms:
            # Managed Object
            mo = ManagedObject.get_by_id(int(ai.managed_object))
            if not mo:
                self.logger.error("Invalid managed object: %s", ai.managed_object)
                return
            mos[ai.managed_object] = mo
            # Timestamp
            if ai.timestamp:
                tses[ai.timestamp] = self.parse_timestamp(ai.timestamp)
            # Alarm class
            alarm_class = AlarmClass.get_by_name(ai.alarm_class)
            if not alarm_class:
                self.logger.error("Invalid alarm class: %s", ai.alarm_class)
                return
            alarm_classes[ai.alarm_class] = alarm_class
        #
        now = datetime.datetime.now()
        if not group_alarm:
            # Create group alarm
            # Calculate timestamp and managed object
            mo_id = req.alarms[0].managed_object
            min_ts = now
            for ai in req.alarms:
                if not ai.timestamp:
                    continue
                ts = tses[ai.timestamp]
                if ts < min_ts:
                    mo_id = ai.managed_object
                    min_ts = ts
            # Resolve managed object
            mo = mos[mo_id]
            # Get group alarm's alarm class
            if req.alarm_class:
                alarm_class = AlarmClass.get_by_name(req.alarm_class)
                if not alarm_class:
                    self.logger.error("Invalid group alarm class: %s", req.alarm_class)
                    return
            else:
                alarm_class = CAlarmRule.get_default_alarm_class()
            # Raise group alarm
            group_alarm = await self.raise_alarm(
                managed_object=mo,
                timestamp=min_ts,
                alarm_class=alarm_class,
                vars={"name": req.name or "Group"},
                reference=req.reference,
                labels=req.labels or [],
            )
        # Fetch all open alarms in group
        open_alarms: Dict[bytes, ActiveAlarm] = {
            alarm.reference: alarm
            for alarm in ActiveAlarm.objects.filter(groups__in=[group_alarm.reference])
        }
        seen_refs: Set[bytes] = set()
        for ai in req.alarms:
            h_ref = self.get_reference_hash(ai.reference)
            if h_ref in open_alarms:
                seen_refs.add(h_ref)
                continue  # Alarm is still active, skipping
            r_vars = ai.vars or {}
            if ai.labels:
                r_vars.update(alarm_classes[ai.alarm_class].convert_labels_var(ai.labels))
            # Raise new alarm
            await self.raise_alarm(
                managed_object=mos[ai.managed_object],
                timestamp=tses[ai.timestamp] if ai.timestamp else now,
                alarm_class=alarm_classes[ai.alarm_class],
                vars=r_vars,
                reference=ai.reference,
                groups=[
                    GroupItem(
                        reference=req.reference,
                        alarm_class=group_alarm.alarm_class,
                        title=req.name or "Group",
                    )
                ],
                labels=ai.labels,
            )
        # Close hanging alarms
        for h_ref in set(open_alarms) - seen_refs:
            await self.clear_by_reference(h_ref, ts=now)

    async def on_msg_set_status(self, req: SetStatusRequest) -> None:
        """
        Process `ensure_group` message.
        """
        ac = AlarmClass.get_by_name(self.AVAIL_CLS)

        for item in req.statuses:
            mo = self.parse_object(item.managed_object)
            if not mo:
                continue
            ts = self.parse_timestamp(item.timestamp)
            self.set_status(mo.id, item.status, ts)
            # @todo bulk alarm method
            ref = f"p:{mo.id}"
            try:
                if item.status:
                    await self.clear_by_reference(ref, ts=ts)
                else:
                    await self.raise_alarm(
                        managed_object=mo,
                        timestamp=ts,
                        alarm_class=ac,
                        reference=ref,
                        vars={},
                        labels=item.labels,
                    )
            except Exception:
                metrics["alarm_dispose_error"] += 1
                error_report()
            finally:
                if self.topo_rca_lock:
                    # Release pending RCA Lock
                    await self.topo_rca_lock.release()
                    self.topo_rca_lock = None

    async def clear_by_id(
        self,
        id: Union[str, bytes],
        ts: Optional[datetime.datetime] = None,
        message: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        """
        Clear alarm by id
        """
        ts = ts or datetime.datetime.now()
        # Get alarm
        alarm = ActiveAlarm.objects.filter(pk=id).first()
        if not alarm:
            self.logger.info("Alarm '%s' is not found. Skipping", id)
            return
        # Clear alarm
        self.logger.info(
            "[%s|%s] Clear alarm %s(%s): %s",
            alarm.managed_object.name,
            alarm.managed_object.address,
            alarm.alarm_class.name,
            alarm.id,
            message or "by id",
        )
        alarm.last_update = max(alarm.last_update, ts)
        groups = alarm.groups
        alarm.clear_alarm(message or "Cleared by id", ts=ts, source=source)
        metrics["alarm_clear"] += 1
        await self.clear_groups(groups, ts=ts)

    async def clear_by_reference(
        self,
        reference: Union[str, bytes],
        ts: Optional[datetime.datetime] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Clear alarm by reference
        """
        ts = ts or datetime.datetime.now()
        # Normalize reference
        if isinstance(reference, str):
            ref_hash = self.get_reference_hash(reference)
        else:
            ref_hash = reference
        # Get alarm
        alarm = ActiveAlarm.objects.filter(reference=ref_hash).first()
        if not alarm:
            self.logger.info("Alarm '%s' is not found. Skipping", reference)
            return
        # Clear alarm
        self.logger.info(
            "[%s|%s] Clear alarm %s(%s): %s",
            alarm.managed_object.name,
            alarm.managed_object.address,
            alarm.alarm_class.name,
            alarm.id,
            message or f"by reference {reference}",
        )
        alarm.last_update = max(alarm.last_update, ts)
        groups = alarm.groups
        alarm.clear_alarm(message or "Cleared by reference", ts=ts)
        metrics["alarm_clear"] += 1
        await self.clear_groups(groups, ts=ts)

    async def dispose_event(self, e: Event):
        """
        Dispose event according to disposition rule
        """

        def save_to_disposelog(action: str, a: Optional[ActiveAlarm] = None):
            # Send dispose information to clickhouse
            data = {
                "date": e.timestamp.date(),
                "ts": e.timestamp,
                "event_id": str(e.id),
                "alarm_id": str(a.id) if a else None,
                "op": action,
                "managed_object": managed_object.bi_id,
                "target_reference": e.target.reference,
                "target": e.target.model_dump(exclude={"is_agent"}),
                "event_class": event_class.bi_id,
                "alarm_class": a.alarm_class.bi_id if a else None,
                "reopens": a.reopens if a else 0,
            }
            self.register_metrics("disposelog", [data])

        event_id = str(e.id)
        self.logger.info("[%s] Disposing", event_id)
        event_class = EventClass.get_by_name(e.type.event_class)
        drc = self.rules.get(event_class.id)
        managed_object = ManagedObject.get_by_id(int(e.target.id))
        if not drc:
            self.logger.info(
                "[%s] No disposition rules for class %s, skipping", event_id, event_class.name
            )
            return
        # Apply disposition rules
        for rule in drc:
            if not self.eval_expression(rule.condition, event=e):
                continue  # Rule is not applicable
            # Process action
            if rule.action == "drop":
                self.logger.info("[%s] Dropped by action", event_id)
                # e.delete()
                save_to_disposelog("drop")
                return
            elif rule.action == "ignore":
                self.logger.info("[%s] Ignored by action", event_id)
                save_to_disposelog("ignore")
                return
            elif rule.action == "raise" and rule.combo_condition == "none":
                alarm = await self.raise_alarm_from_rule(rule, e, managed_object)
                save_to_disposelog("raise", alarm)
            elif rule.action == "clear" and rule.combo_condition == "none":
                alarm = await self.clear_alarm_from_rule(rule, e, managed_object)
                save_to_disposelog("clear", alarm)
            if rule.action in ("raise", "clear"):
                # Write reference if can trigger delayed event
                if rule.unique and rule.event_class.id in self.back_rules:
                    vars = rule.get_vars(e, managed_object)
                    reference = self.get_default_reference(
                        managed_object=managed_object, alarm_class=rule.alarm_class, vars=vars
                    )
                    e.reference = self.get_reference_hash(reference)
                    # e.save()
                # Process delayed combo conditions
                if event_class.id in self.back_rules:
                    for br in self.back_rules[event_class.id]:
                        de = self.get_delayed_event(br, e, managed_object)
                        if de:
                            if br.action == "raise":
                                alarm = await self.raise_alarm_from_rule(br, de, managed_object)
                                save_to_disposelog("raise", alarm)
                            elif br.action == "clear":
                                alarm = await self.clear_alarm_from_rule(br, de, managed_object)
                                save_to_disposelog("clear", alarm)
            if rule.stop_disposition:
                break
        self.logger.info("[%s] Disposition complete", event_id)

    async def topology_rca(self, alarm: ActiveAlarm):
        """
        Topology-based RCA
        :param alarm:
        :return:
        """

        def can_correlate(a1, a2):
            """
            Check if alarms can be correlated together (within corellation window)
            :param a1:
            :param a2:
            :return:
            """
            return (
                not config.correlator.topology_rca_window
                or (a1.timestamp - a2.timestamp).total_seconds()
                <= config.correlator.topology_rca_window
            )

        def all_uplinks_failed(a1):
            """
            Check if all uplinks for alarm is failed
            :param a1:
            :return:
            """
            if not a1.uplinks:
                return False
            return sum(1 for mo in a1.uplinks if mo in neighbor_alarms) == len(a1.uplinks)

        def get_root(a1) -> Optional[ActiveAlarm]:
            """
            Get root cause for failed uplinks.
            Considering all uplinks are failed.
            Uplinks are ordered according to path length.
            Return first applicable

            :param a1:
            :return:
            """
            for u in a1.uplinks:
                na = neighbor_alarms[u]
                if can_correlate(a1, na):
                    return na
            return None

        def get_neighboring_alarms(ca: ActiveAlarm) -> Dict[int, ActiveAlarm]:
            r = {
                na.managed_object.id: na
                for na in ActiveAlarm.objects.filter(
                    alarm_class=ca.alarm_class.id,
                    rca_neighbors__in=[ca.managed_object.id] + ca.uplinks,
                )
            }
            # Add current alarm to correlate downlink alarms properly
            r[alarm.managed_object.id] = ca
            return r

        def iter_downlink_alarms(a1):
            """
            Yield all downlink alarms
            :param a1:
            :return:
            """
            mo = a1.managed_object.id
            for na in neighbor_alarms.values():
                if na.uplinks and mo in na.uplinks:
                    yield na

        def correlate_uplinks(ca: ActiveAlarm) -> bool:
            """
            Correlate with uplink alarms if all uplinks are faulty.
            :param ca:
            :return:
            """
            if not all_uplinks_failed(ca):
                return False
            self.logger.info("[%s] All uplinks are faulty. Correlating", ca.id)
            ra = get_root(ca)
            if not ra:
                return False
            self.logger.info("[%s] Set root to %s", ca.id, ra.id)
            ca.set_root(ra, rca_type=RCA_TOPOLOGY)
            metrics["alarm_correlated_topology"] += 1
            return True

        def correlate_merge_downlinks(ca: ActiveAlarm) -> bool:
            """
            Donwlink merge correlation
            :param ca:
            :return:
            """
            if not ca.uplinks or not ca.rca_neighbors:
                return False
            dlm_neighbors = {mo: w for mo, w in zip(ca.rca_neighbors, ca.dlm_windows) if w > 0}
            dlm_candidates = set(neighbor_alarms) & set(dlm_neighbors)
            if not dlm_candidates:
                return False
            # Get possible candidates
            t0 = ca.timestamp
            candidates = list(
                sorted(
                    (
                        neighbor_alarms[mo]
                        for mo in dlm_candidates
                        if (t0 - neighbor_alarms[mo].timestamp).total_seconds() <= dlm_neighbors[mo]
                    ),
                    key=operator.attrgetter("timestamp"),
                )
            )
            if not candidates:
                return False
            ra = candidates[0]
            self.logger.info("[%s] Set root to %s (downlink merge)", ca.id, ra.id)
            ca.set_root(ra, rca_type=RCA_DOWNLINK_MERGE)
            metrics["alarm_correlated_topology"] += 1
            return True

        self.logger.debug("[%s] Topology RCA", alarm.id)
        # Acquire lock
        if self.is_distributed and alarm.managed_object.rca_neighbors:
            # Set lock until the end of dispose
            mo = alarm.managed_object
            self.topo_rca_lock = RCALock(mo.rca_neighbors + [mo.id])
            self.logger.debug("[%s] Acquire lock: %s", alarm.id, mo.rca_neighbors)
            await self.topo_rca_lock.acquire()
        self.logger.debug("[%s] Get neighboring alarms", alarm.id)
        # Get neighboring alarms
        neighbor_alarms = get_neighboring_alarms(alarm)
        # Correlate current alarm
        correlate_uplinks(alarm) or correlate_merge_downlinks(alarm)
        # Correlate all downlink alarms
        for a in iter_downlink_alarms(alarm):
            correlate_uplinks(a)
        self.logger.debug("[%s] Correlation completed", alarm.id)

    @classmethod
    def get_group_deferred_count(
        cls, h_ref: bytes, min_ts: datetime.datetime, max_ts: datetime.datetime
    ) -> int:
        """
        Get amount of waiting alarms for reference
        """
        for doc in ActiveAlarm._get_collection().aggregate(
            [
                {
                    "$match": {
                        "deferred_groups": h_ref,
                        "timestamp": {"$gte": min_ts, "$lte": max_ts},
                    }
                },
                {"$group": {"_id": None, "def_count": {"$sum": 1}}},
                {"$project": {"_id": 0}},
            ]
        ):
            return doc.get("def_count", 0) or 0
        return 0

    def resolve_deferred_groups(self, h_ref: bytes) -> None:
        """
        Mark all resolved groups as permanent
        """
        ActiveAlarm._get_collection().update_many(
            {"deferred_groups": {"$in": [h_ref]}},
            {"$push": {"groups": h_ref}, "$pullAll": {"deferred_groups": [h_ref]}},
        )
        # Reset affected cached values
        with ref_lock:
            deprecated: List[Tuple[str]] = [
                a_ref
                for a_ref, alarm in self._reference_cache.items()
                if alarm and alarm.deferred_groups and h_ref in alarm.deferred_groups
            ]
            for a_ref in deprecated:
                del self._reference_cache[a_ref]

    async def get_groups(
        self, alarm: ActiveAlarm, groups: Iterable[GroupItem]
    ) -> Tuple[List[ActiveAlarm], List[bytes]]:
        """
        Resolve all groups and create when necessary

        :param alarm: Active Alarm to match groups
        :param groups: Iterable of group configurations
        :returns: Tuple of list of active group alarms
                  and the list of the deferred group references
        """
        active: List[ActiveAlarm] = []
        deferred: List[bytes] = []
        for group in groups:
            if group.reference == alarm.raw_reference:
                continue  # Reference cycle
            def_h_ref: Optional[bytes] = None
            # Fetch or raise group alarm
            g_alarm = self.get_by_reference(group.reference)
            if not g_alarm:
                if group.min_threshold > 0 and group.window > 0:
                    # Check group has enough deferred alarms to raise thresholds
                    h_ref = self.get_reference_hash(group.reference)
                    w_delta = datetime.timedelta(seconds=group.window)
                    n_waiting = self.get_group_deferred_count(
                        h_ref, alarm.timestamp - w_delta, alarm.timestamp + w_delta
                    )
                    if n_waiting < group.min_threshold - 1:
                        # Below the threshold, set group as deferred
                        deferred.append(h_ref)
                        continue
                    else:
                        # Pull deferred alarms later
                        def_h_ref = h_ref
                # Raise group alarm
                g_alarm = await self.raise_alarm(
                    managed_object=alarm.managed_object,
                    timestamp=alarm.timestamp,
                    alarm_class=group.alarm_class,
                    vars={"name": group.title},
                    reference=group.reference,
                    labels=group.labels,
                    min_group_size=group.max_threshold,
                )
                if g_alarm:
                    # Update cache
                    self._reference_cache[(group.reference,)] = g_alarm
            if g_alarm:
                active.append(g_alarm)
                if def_h_ref:
                    self.resolve_deferred_groups(def_h_ref)
        # Service groups
        for svc_id in alarm.affected_services:
            ref = f"{SVC_REF_PREFIX}:{svc_id}"
            sg_alarm = self.get_by_reference(ref)
            if sg_alarm:
                active.append(sg_alarm)
                continue
            # s_ref = self.get_reference_hash(ref)
            if alarm.raw_reference != ref:
                deferred.append(self.get_reference_hash(ref))
        return active, deferred

    async def clear_groups(self, groups: List[bytes], ts: Optional[datetime.datetime]) -> None:
        """
        Clear group alarms from list when necessary

        @todo: Possible race when called from different processes

        :param groups: List of group reference hashes
        :param ts: Clear timestamp
        """
        # Get groups summary
        r: Dict[bytes, int] = {}
        group_settings: Dict[bytes, int] = {}
        coll = ActiveAlarm._get_collection()
        for doc in coll.aggregate(
            [
                # Filter all active alarms in the selected groups
                {"$match": {"groups": {"$in": groups}}},
                # Leave only `groups` field
                {"$project": {"groups": 1}},
                # Unwind `groups` array to separate documents
                {"$unwind": "$groups"},
                # Group by each group reference
                {"$group": {"_id": "$groups", "n": {"$sum": 1}}},
            ]
        ):
            r[doc["_id"]] = doc["n"]
        # Group Settings
        for doc in coll.find(
            # Filter all active alarms in the selected groups
            {"reference": {"$in": groups}},
            {"reference": 1, "min_group_size": 1},
        ):
            group_settings[doc["reference"]] = doc.get("min_group_size", 0)
        left: List[bytes] = []
        for ref in groups:
            self.logger.debug("[%s] Check group size: %s", ref, group_settings.get(ref, 0))
            if r.get(ref, 0) <= group_settings.get(ref, 0):
                self.logger.info(
                    "Clear empty group %r, minimal size: %s", ref, group_settings.get(ref, 0)
                )
                await self.clear_by_reference(ref, ts=ts)
                coll.update_many({"groups": {"$in": [ref]}}, {"$pull": {"groups": {"$in": [ref]}}})
                # @todo Update datastream ?
            else:
                left.append(ref)
        if left:
            await self.update_groups_summary(left)

    async def update_groups_summary(self, refs: Iterable[bytes]) -> None:
        """
        Recalculate summaries for all changed groups defined by references

        :param refs: Iterable of group reference hashes
        """

        def update_totals(totals, group_refs, summary):
            if not group_refs or not summary:
                return
            for g_ref in group_refs:
                for si in summary:
                    totals[g_ref][si["profile"]] += si["summary"]

        all_groups = list(refs)
        if not all_groups:
            return
        total_objects: DefaultDict[bytes, DefaultDict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        total_services: DefaultDict[bytes, DefaultDict[ObjectId, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        total_subscribers: DefaultDict[bytes, DefaultDict[ObjectId, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for doc in ActiveAlarm._get_collection().find(
            {"groups": {"$in": list(all_groups)}},
            {
                "_id": 0,
                "groups": 1,
                "direct_objects": 1,
                "direct_services": 1,
                "direct_subscribers": 1,
            },
        ):
            groups = doc.get("groups", [])
            if not groups:
                continue
            update_totals(total_objects, groups, doc.get("direct_objects", []))
            update_totals(total_services, groups, doc.get("direct_services", []))
            update_totals(total_subscribers, groups, doc.get("direct_subscribers", []))
        # Perform bulk update
        bulk = [
            UpdateOne(
                {"reference": ref},
                {
                    "$set": {
                        "total_objects": [
                            si.to_mongo()
                            for si in ObjectSummaryItem.dict_to_items(total_objects[ref])
                        ],
                        "total_services": [
                            si.to_mongo() for si in SummaryItem.dict_to_items(total_services[ref])
                        ],
                        "total_subscribers": [
                            si.to_mongo()
                            for si in SummaryItem.dict_to_items(total_subscribers[ref])
                        ],
                    }
                },
            )
            for ref in all_groups
        ]
        ActiveAlarm._get_collection().bulk_write(bulk)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_reference_cache"), lock=lambda _: ref_lock)
    def get_by_reference(cls, reference: str) -> Optional["ActiveAlarm"]:
        return ActiveAlarm.objects.filter(reference=cls.get_reference_hash(reference)).first()

    def set_status(self, oid: int, status: bool, ts: Optional[datetime.datetime] = None) -> None:
        """
        Add status changes to
        :param oid: ManagedObject Id for setting status
        :param status: Status True/Flase
        :param ts: Timestamp when change
        :return:
        """
        self.status_changes.append((oid, status, ts))

    async def update_object_statuses(self):
        """
        Update object statuses
        :return:
        """
        from noc.sa.models.managedobject import ManagedObjectStatus

        self.logger.info("Running object status updater")
        while True:
            await asyncio.sleep(config.correlator.object_status_update_interval)
            # Count status changes
            count = len(self.status_changes)
            if not count:
                continue
            r = []
            for _ in range(0, count):
                r.append(self.status_changes.popleft())
            self.logger.info("Updating %d statuses", len(r))
            try:
                ManagedObjectStatus.update_status_bulk(r, update_jobs=True)
            except Exception:
                error_report()
                pass


if __name__ == "__main__":
    CorrelatorService().start()
