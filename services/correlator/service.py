#!./bin/python
# ---------------------------------------------------------------------
# noc-correlator daemon
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys
import datetime
import re
from collections import defaultdict
import threading
from typing import Union, Any, Iterable, Optional, Tuple, Dict, List, Set
import operator
from itertools import chain
from hashlib import sha512

# Third-party modules
import orjson
from bson import ObjectId
from dateutil.parser import parse as parse_date
from pydantic import parse_obj_as, ValidationError
import cachetools

# NOC modules
from noc.config import config
from noc.core.service.tornado import TornadoService
from noc.core.scheduler.scheduler import Scheduler
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.services.correlator.alarmrule import AlarmRuleSet, AlarmRule as CAlarmRule
from noc.services.correlator.rule import Rule
from noc.services.correlator.rcacondition import RCACondition
from noc.services.correlator.trigger import Trigger
from noc.services.correlator.models.disposereq import DisposeRequest
from noc.services.correlator.models.eventreq import EventRequest
from noc.services.correlator.models.clearreq import ClearRequest
from noc.services.correlator.models.raisereq import RaiseRequest
from noc.services.correlator.models.ensuregroupreq import EnsureGroupRequest
from noc.fm.models.eventclass import EventClass
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmlog import AlarmLog
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmtrigger import AlarmTrigger
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.fm.models.alarmdiagnosticconfig import AlarmDiagnosticConfig
from noc.fm.models.alarmrule import AlarmRule
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.servicesummary import ServiceSummary, SummaryItem, ObjectSummaryItem
from noc.core.version import version
from noc.core.debug import format_frames, get_traceback_frames, error_report
from noc.services.correlator import utils
from noc.core.perf import metrics
from noc.core.fm.enum import RCA_RULE, RCA_TOPOLOGY, RCA_DOWNLINK_MERGE
from noc.core.liftbridge.message import Message
from noc.services.correlator.rcalock import RCALock
from services.correlator.alarmrule import GroupItem

ref_lock = threading.Lock()


class CorrelatorService(TornadoService):
    name = "correlator"
    pooled = True
    use_mongo = True
    process_name = "noc-%(name).10s-%(pool).5s"

    _reference_cache = cachetools.TTLCache(100, ttl=60)

    def __init__(self):
        super().__init__()
        self.version = version.version
        self.rules: Dict[ObjectId, List[Rule]] = {}
        self.back_rules: Dict[ObjectId, List[Rule]] = {}
        self.triggers: Dict[ObjectId, List[Trigger]] = {}
        self.rca_forward = {}  # alarm_class -> [RCA condition, ..., RCA condititon]
        self.rca_reverse = defaultdict(set)  # alarm_class -> set([alarm_class])
        self.alarm_rule_set = AlarmRuleSet()
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

    def mark_as_failed(self, event: "ActiveEvent"):
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
        event: ActiveEvent = None,
    ) -> Optional[ActiveAlarm]:
        """
        Try to reopen archived alarm

        :param managed_object: Managed Object instance
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
                event.event_class.name,
                arch.alarm_class.name,
                arch.id,
            )
            reason = f"Reopened by {event.event_class.name}({event.id})"
        else:
            reason = "Reopened by alarm"
        alarm = arch.reopen(reason)
        metrics["alarm_reopen"] += 1
        return alarm

    def refresh_alarm(self, alarm: ActiveAlarm, timestamp: datetime.datetime):
        """
        Refresh active alarm data
        """
        if timestamp < alarm.timestamp:
            # Set to earlier date
            alarm.timestamp = timestamp
            alarm.save()
        elif timestamp > alarm.last_update:
            # Refresh last update
            alarm.last_update = timestamp
            alarm.save()

    async def raise_alarm(
        self,
        managed_object: ManagedObject,
        timestamp: datetime.datetime,
        alarm_class: AlarmClass,
        vars: Optional[Dict[str, Any]],
        event: Optional[ActiveEvent] = None,
        reference: Optional[str] = None,
        remote_system: Optional[RemoteSystem] = None,
        remote_id: Optional[str] = None,
        groups: Optional[List[GroupItem]] = None,
        labels: Optional[List[str]] = None,
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
        :returns: Alarm, if created, None otherwise
        """
        scope_label = str(event.id) if event else "DIRECT"
        labels = labels or []
        # @todo: Make configurable
        if not managed_object.is_managed:
            self.logger.info("Managed object is not managed. Do not raise alarm")
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
                    f"event {event.event_class.name}" if event else "DIRECT",
                    alarm.alarm_class.name,
                    alarm.id,
                )
                if event:
                    event.contribute_to_alarm(alarm)
                    metrics["alarm_contribute"] += 1
                self.refresh_alarm(alarm, timestamp)
                return alarm
        # Calculate alarm coverage
        summary = ServiceSummary.get_object_summary(managed_object)
        summary["object"] = {managed_object.object_profile.id: 1}
        #
        severity = max(ServiceSummary.get_severity(summary), 1)
        # @todo: Fix
        self.logger.info(
            "[%s|%s|%s] Calculated alarm severity is: %s",
            scope_label,
            managed_object.name,
            managed_object.address,
            severity,
        )
        # Create new alarm
        direct_services = SummaryItem.dict_to_items(summary["service"])
        direct_subscribers = SummaryItem.dict_to_items(summary["subscriber"])
        if event:
            msg = f"Alarm risen from event {event.id}({event.event_class.name})"
        else:
            msg = "Alarm risen directly"
        a = ActiveAlarm(
            timestamp=timestamp,
            last_update=timestamp,
            managed_object=managed_object.id,
            alarm_class=alarm_class,
            severity=severity,
            vars=vars,
            reference=ref_hash,
            direct_services=direct_services,
            direct_subscribers=direct_subscribers,
            total_objects=ObjectSummaryItem.dict_to_items(summary["object"]),
            total_services=direct_services,
            total_subscribers=direct_subscribers,
            log=[
                AlarmLog(
                    timestamp=datetime.datetime.now(),
                    from_status="A",
                    to_status="A",
                    message=msg,
                )
            ],
            opening_event=event.id if event else None,
            labels=labels,
            remote_system=remote_system,
            remote_id=remote_id,
        )
        a.effective_labels = list(chain.from_iterable(ActiveAlarm.iter_effective_labels(a)))
        a.raw_reference = reference
        # Static groups
        alarm_groups: Dict[str, GroupItem] = {}
        if groups:
            for gi in groups:
                if gi.reference and gi.reference not in alarm_groups:
                    alarm_groups[gi.reference] = gi
        # Apply rules
        for rule in self.alarm_rule_set.iter_rules(a):
            for gi in rule.iter_groups(a):
                if gi.reference and gi.reference not in alarm_groups:
                    alarm_groups[gi.reference] = gi
        all_groups, deferred_groups = await self.get_groups(a, alarm_groups.values())
        a.groups = [g.reference for g in all_groups]
        a.deferred_groups = deferred_groups
        # Save
        a.save()
        if event:
            event.contribute_to_alarm(a)
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
        if not a.root:
            a.managed_object.event(
                a.managed_object.EV_ALARM_RISEN,
                {
                    "alarm": a,
                    "subject": a.subject,
                    "body": a.body,
                    "symptoms": a.alarm_class.symptoms,
                    "recommended_actions": a.alarm_class.recommended_actions,
                    "probable_causes": a.alarm_class.probable_causes,
                },
                delay=a.alarm_class.get_notification_delay(),
            )
        # Gather diagnostics when necessary
        AlarmDiagnosticConfig.on_raise(a)
        # Watch for escalations, when necessary
        if config.correlator.auto_escalation and not a.root:
            AlarmEscalation.watch_escalations(a)
        return a

    async def raise_alarm_from_rule(self, rule: Rule, event: ActiveEvent):
        """
        Raise alarm from incoming event
        """
        # Find effective managed object
        managed_object = self.eval_expression(rule.managed_object, event=event)
        if not managed_object:
            self.logger.info("Empty managed object, ignoring")
            return
        if event.managed_object.id != managed_object.id:
            metrics["alarm_change_mo"] += 1
            self.logger.info("Changing managed object to %s", managed_object.name)
        # Extract variables
        vars = rule.get_vars(event)
        await self.raise_alarm(
            managed_object=managed_object,
            timestamp=event.timestamp,
            alarm_class=rule.alarm_class,
            vars=vars,
            event=event,
        )

    async def correlate(self, a: ActiveAlarm):
        # Topology RCA
        if a.alarm_class.topology_rca:
            await self.topology_rca(a)
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

    async def clear_alarm_from_rule(self, rule: "Rule", event: "ActiveEvent"):
        managed_object = self.eval_expression(rule.managed_object, event=event)
        if not managed_object:
            self.logger.info(
                "[%s|Unknown|Unknown] Referred to unknown managed object, ignoring", event.id
            )
            metrics["unknown_object"] += 1
            return
        if not rule.unique:
            return
        vars = rule.get_vars(event)
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
            event.event_class.name,
            alarm.alarm_class.name,
            alarm.id,
        )
        event.contribute_to_alarm(alarm)
        alarm.closing_event = event.id
        alarm.last_update = max(alarm.last_update, event.timestamp)
        groups = alarm.groups
        alarm.clear_alarm("Cleared by disposition rule '%s'" % rule.u_name, ts=event.timestamp)
        metrics["alarm_clear"] += 1
        await self.clear_groups(groups, ts=event.timestamp)

    def get_delayed_event(self, rule: Rule, event: ActiveEvent):
        """
        Check wrether all delayed conditions are met

        :param rule: Delayed rule
        :param event: Event which can trigger delayed rule
        """
        # @todo: Rewrite to scheduler
        vars = rule.get_vars(event)
        reference = self.get_default_reference(
            managed_object=event.managed_object, alarm_class=rule.alarm_class, vars=vars
        )
        ref_hash = self.get_reference_hash(reference)
        ws = event.timestamp - datetime.timedelta(seconds=rule.combo_window)
        de = ActiveEvent.objects.filter(
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
            for ee in ActiveEvent.objects.filter(
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
        data = orjson.loads(msg.value)
        # Backward-compatibility
        if "$op" not in data:
            data["$op"] = "event"
        # Parse request
        try:
            req = parse_obj_as(DisposeRequest, data)
        except ValidationError as e:
            self.logger.error("Malformed message: %s", e)
            metrics["malformed_messages"] += 1
            return
        # Call handler, may not be invalid
        msg_handler = getattr(self, f"on_msg_{req.op}")
        if not msg_handler:
            self.logger.error("Internal error. No handler for '%s'", req.op)
            return
        await msg_handler(req)
        metrics["alarm_dispose"] += 1

    async def on_msg_event(self, req: EventRequest) -> None:
        """
        Process `event` message type
        """
        self.logger.info("[event|%s] Receiving message", req.event_id)
        try:
            event = ActiveEvent.from_json(req.event)
            event.timestamp = event.timestamp.replace(tzinfo=None)
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
        ts = parse_date(req.timestamp) if req.timestamp else datetime.datetime.now()
        # Managed Object
        managed_object = ManagedObject.get_by_id(int(req.managed_object))
        if not managed_object:
            self.logger.error("Invalid managed object: %s", req.managed_object)
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
        try:
            await self.raise_alarm(
                managed_object=managed_object,
                timestamp=ts,
                alarm_class=alarm_class,
                vars=req.vars,
                reference=req.reference,
                groups=groups,
                labels=req.labels or [],
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

    async def on_msg_clear(self, req: ClearRequest) -> None:
        """
        Process `clear` message.
        """
        # Fetch timestamp
        ts = parse_date(req.timestamp) if req.timestamp else datetime.datetime.now()
        await self.clear_by_reference(req.reference, ts)

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
                tses[ai.timestamp] = parse_date(ai.timestamp)
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
            # Raise new alarm
            await self.raise_alarm(
                managed_object=mos[ai.managed_object],
                timestamp=tses[ai.timestamp] if ai.timestamp else now,
                alarm_class=alarm_classes[ai.alarm_class],
                vars=ai.vars or {},
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

    async def clear_by_reference(
        self, reference: Union[str, bytes], ts: Optional[datetime.datetime] = None
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
            "[%s|%s] Clear alarm %s(%s) by reference %s",
            alarm.managed_object.name,
            alarm.managed_object.address,
            alarm.alarm_class.name,
            alarm.id,
            reference,
        )
        alarm.last_update = max(alarm.last_update, ts)
        groups = alarm.groups
        alarm.clear_alarm("Cleared by reference")
        metrics["alarm_clear"] += 1
        await self.clear_groups(groups, ts=ts)

    async def dispose_event(self, e: ActiveEvent):
        """
        Dispose event according to disposition rule
        """
        event_id = str(e.id)
        self.logger.info("[%s] Disposing", event_id)
        drc = self.rules.get(e.event_class.id)
        if not drc:
            self.logger.info(
                "[%s] No disposition rules for class %s, skipping", event_id, e.event_class.name
            )
            return
        # Apply disposition rules
        for rule in drc:
            if not self.eval_expression(rule.condition, event=e):
                continue  # Rule is not applicable
            # Process action
            if rule.action == "drop":
                self.logger.info("[%s] Dropped by action", event_id)
                e.delete()
                return
            elif rule.action == "ignore":
                self.logger.info("[%s] Ignored by action", event_id)
                return
            elif rule.action == "raise" and rule.combo_condition == "none":
                await self.raise_alarm_from_rule(rule, e)
            elif rule.action == "clear" and rule.combo_condition == "none":
                await self.clear_alarm_from_rule(rule, e)
            if rule.action in ("raise", "clear"):
                # Write reference if can trigger delayed event
                if rule.unique and rule.event_class.id in self.back_rules:
                    vars = rule.get_vars(e)
                    reference = self.get_default_reference(
                        managed_object=e.managed_object, alarm_class=rule.alarm_class, vars=vars
                    )
                    e.reference = self.get_reference_hash(reference)
                    e.save()
                # Process delayed combo conditions
                if e.event_class.id in self.back_rules:
                    for br in self.back_rules[e.event_class.id]:
                        de = self.get_delayed_event(br, e)
                        if de:
                            if br.action == "raise":
                                await self.raise_alarm_from_rule(br, de)
                            elif br.action == "clear":
                                await self.clear_alarm_from_rule(br, de)
            if rule.stop_disposition:
                break
        self.logger.info("[%s] Disposition complete", event_id)

    async def topology_rca(self, alarm):
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
                    alarm_class=ca.alarm_class.id, rca_neighbors__in=[ca.managed_object.id]
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
            :param a1:
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
        if self.is_distributed:
            # Set lock until the end of dispose
            mo = alarm.managed_object
            self.topo_rca_lock = RCALock(mo.data.rca_neighbors + [mo.id])
            await self.topo_rca_lock.acquire()
        # Get neighboring alarms
        neighbor_alarms = get_neighboring_alarms(alarm)
        # Correlate current alarm
        correlate_uplinks(alarm) or correlate_merge_downlinks(alarm)
        # Correlate all downlink alarms
        for a in iter_downlink_alarms(alarm):
            correlate_uplinks(a)
        self.logger.debug("[%s] Correlation completed", alarm.id)

    def get_group_deferred_count(
        self, h_ref: bytes, min_ts: datetime.datetime, max_ts: datetime.datetime
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
            {"deferred_group": h_ref},
            {"$push": {"groups": h_ref}, "$pullAll": {"deferred_groups": [h_ref]}},
        )
        # Reset affected cached values
        with ref_lock:
            deprecated: List[str] = [
                a_ref
                for a_ref, alarm in self._reference_cache.items()
                if alarm.deferred_groups and h_ref in alarm.deferred_groups
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
                )
                if not g_alarm:
                    # Update cache
                    self._reference_cache[group.reference] = g_alarm
            if g_alarm:
                active.append(g_alarm)
                if def_h_ref:
                    self.resolve_deferred_groups(def_h_ref)
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
        for doc in ActiveAlarm._get_collection().aggregate(
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
        for ref in groups:
            if r.get(ref, 0) == 0:
                self.logger.info("Clear empty group %r", ref)
                await self.clear_by_reference(ref, ts=ts)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_reference_cache"), lock=lambda _: ref_lock)
    def get_by_reference(cls, reference: str) -> Optional["ActiveAlarm"]:
        return ActiveAlarm.objects.filter(reference=cls.get_reference_hash(reference)).first()


if __name__ == "__main__":
    CorrelatorService().start()
