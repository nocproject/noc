# ----------------------------------------------------------------------
# Automation with processed alarm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import operator
import time
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Iterable, Optional, Dict, Any, DefaultDict, Union

# Third-party modules
from bson import ObjectId


# NOC modules
from noc.core.span import get_current_span
from noc.core.span import Span, PARENT_SAMPLE
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.log import PrefixLoggerAdapter
from noc.core.perf import metrics
from noc.core.runner.job import Job
from noc.core.debug import error_report
from noc.core.tt.types import (
    EscalationGroupPolicy,
    EscalationRequest,
    Action as ActionReq,
)
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.sa.models.serviceprofile import ServiceProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from noc.services.escalator.alarmaction import GroupAction
from noc.services.escalator.types import JobStatus, ActionStatus, ItemStatus
from noc.services.escalator.actionlog import ActionLog, ActionResult
from noc.maintenance.models.maintenance import Maintenance


@dataclass
class GroupItem(object):
    reference: bytes
    id: Optional[str] = None


@dataclass
class Item(object):
    """Over Job Item"""

    #! Replace to alarm List, status
    alarm: Union[ActiveAlarm, ArchivedAlarm]
    status: ItemStatus = ItemStatus.NEW

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return self.alarm.managed_object

    def get_state(self):
        return {"alarm": self.alarm.id, "status": self.status.value}


class AlarmAutomationJob(Job):
    """
    Runtime Alarm Automation
    """

    lock = ProcessLock(category="escalator", owner="escalator")

    def __init__(
        self,
        name: str,
        status: JobStatus,
        items: List[Item],
        actions: List[ActionLog],
        groups: Optional[List[GroupItem]] = None,
        end_condition: str = "CR",
        maintenance_policy: str = None,
        policy: EscalationGroupPolicy = EscalationGroupPolicy.ROOT,
        # Repeat
        max_repeat: int = 0,
        repeat_delay: int = 60,
        # Span Context
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        # Id document
        tt_docs: Dict[str, str] = None,
        id: Optional[str] = None,
        logger: Optional[Any] = None,
        dry_run: bool = False,
        static_delay: Optional[int] = None,
    ):
        super().__init__(id=id, name=name, status=status)
        self.items: List[Item] = items
        self.policy = policy or EscalationGroupPolicy.ROOT
        self.groups: List[GroupItem] = groups or []
        self.actions = actions
        self.end_condition = end_condition or "CR"
        self.maintenance_policy = maintenance_policy or "e"
        # Repeat
        self.max_repeat = max_repeat
        self.repeat_delay = repeat_delay
        # Span
        self.ctx_id = ctx_id
        self.telemetry_sample = telemetry_sample
        self.dry_run = dry_run
        self.static_delay: Optional[str] = static_delay
        # Stats
        self.tt_docs: Dict[str, str] = tt_docs or {}  # TTSystem -> doc_id
        self.alarm_log = []
        # self.end_at: Optional[datetime.datetime] = None
        self.affected_services = []
        # Alarm Severity
        self.severity = self.alarm.severity
        self.total_objects = []
        self.total_services = []
        self.total_subscribers = []
        self.logger = logger or PrefixLoggerAdapter(
            logging.getLogger(__name__), f"[{self.id}|{self.leader_item.alarm}"
        )

    @property
    def leader_item(self) -> "Item":
        """Return first item"""
        return self.items[0]

    @property
    def alarm(self) -> ActiveAlarm:
        """Getting document alarm"""
        return self.leader_item.alarm

    def run(self, actions: Optional[List[ActionLog]] = None):
        """
        Run Job
        Iterate over jobs, and run it
        Repeating Job
        Return Job status and Next timestamp
        """
        is_end = self.check_end()
        now = datetime.datetime.now()
        actions = actions or []
        self.logger.info("Start actions at: %s, End Flag: %s", now, is_end)
        self.update_items()
        self.logger.debug(
            "Processed items: %s, services: %s, groups: %s",
            self.items,
            self.affected_services,
            self.groups,
        )
        runner = GroupAction(self.items, services=self.affected_services, logger=self.logger)
        esc_ctx = self.get_ctx()
        with (
            Span(
                client="escalator",
                sample=self.get_span_sample(),
                context=self.ctx_id,
            ),
            self.lock.acquire(self.get_lock_items()),
            change_tracker.bulk_changes(),
        ):
            if not self.ctx_id:
                # span_ctx.span_context
                self.set_escalation_context()
            # Sorted by ts
            for aa in sorted(actions[:] + self.actions, key=operator.attrgetter("timestamp")):
                self.logger.debug("[%s] Processed action", aa)
                if aa.status in [ActionStatus.SUCCESS, ActionStatus.FAILED]:
                    # Skip already running job
                    if self.dry_run:
                        self.logger.debug("[%s] Action already executed. Next...", aa)
                    continue
                elif not aa.is_match(self.severity, now):
                    # Set Skip (Condition)
                    self.logger.debug(
                        "[%s] Action severity condition [%s] not Match. Next...",
                        aa.action,
                        self.severity,
                    )
                    continue
                elif is_end and aa.when != "on_end":
                    self.logger.debug("[%s] Action execute on End. Next...", aa.action)
                    continue
                elif self.dry_run:
                    wait_interval = (now - aa.timestamp).total_seconds()
                    self.logger.info("Dry run mode, waiting interval: %s", wait_interval)
                    if self.static_delay is not None:
                        time.sleep(self.static_delay)
                    # time.sleep(abs(wait_interval) + 1)
                    # time.sleep(10)
                elif aa.timestamp > now:
                    break
                # if not aa.to_run(status, delay):
                #    continue
                try:
                    r = runner.run_action(
                        aa.action,
                        **aa.get_ctx(
                            document_id=self.tt_docs.get(aa.key),
                            action_ctx=esc_ctx,
                        ),
                    )  # aa.get_ctx for job
                except Exception as e:
                    r = ActionResult(status=ActionStatus.FAILED, error=str(e))  # Exception Status
                    error_report()
                    # Job Status to Exception
                self.logger.info("[%s] Action result: %s", aa, r)
                if aa.repeat_num < self.max_repeat and r.status == ActionStatus.SUCCESS:
                    # If Repeat - add action to next on repeat delay
                    # Self register actions
                    self.actions.append(aa.get_repeat(self.repeat_delay))
                aa.set_status(r)
                if r.document_id:
                    self.tt_docs[aa.key] = r.document_id
                # Processed Result
                if aa.stop_processing:
                    # Set Stop job status
                    break
        self.alarm_log += runner.get_bulk()
        if actions:
            # Split one_time actions/sequenced action
            self.actions = actions + self.actions

    @staticmethod
    def summary_to_list(summary, model):
        r = []
        for k in summary:
            p = model.get_by_id(k.profile)
            if not p or getattr(p, "show_in_summary", True) is False:
                continue
            r += [
                {
                    "profile": p.name,
                    "summary": k.summary,
                    "order": (getattr(p, "display_order", 100), -k.summary),
                }
            ]
        return sorted(r, key=operator.itemgetter("order"))

    def get_ctx(self):
        """
        Get escalation context
        """
        # affected_objects = sorted(self.alarm.iter_affected(), key=operator.attrgetter("name"))
        affected_objects = sorted(
            [aa.managed_object for aa in self.items], key=operator.attrgetter("name")
        )
        segment = self.alarm.managed_object.segment
        if segment.is_redundant:
            uplinks = self.alarm.managed_object.uplinks
            lost_redundancy = len(uplinks) > 1
            affected_subscribers = self.summary_to_list(
                segment.total_subscribers, SubscriberProfile
            )
            affected_services = self.summary_to_list(segment.total_services, ServiceProfile)
        else:
            lost_redundancy = False
            affected_subscribers = []
            affected_services = []
        # cons_escalated = [
        #     self.alarm_ids[x.alarm]
        #     for x in self.escalation_doc.consequences
        #     if x.is_already_escalated
        # ]
        # @todo Alarm notification Ctx, Escalation Message Ctx
        return {
            "alarm": self.alarm,
            # "leader": self.alarm,
            "services": self.affected_services,
            "group": "",
            "managed_object": self.alarm.managed_object,
            "affected_objects": affected_objects,
            "cons_escalated": [],
            "total_objects": self.summary_to_list(self.total_objects, ManagedObjectProfile),
            "total_subscribers": self.summary_to_list(self.total_subscribers, SubscriberProfile),
            "total_services": self.summary_to_list(self.total_services, ServiceProfile),
            "tt": None,
            "lost_redundancy": lost_redundancy,
            "affected_subscribers": affected_subscribers,
            "affected_services": affected_services,
            "has_merged_downlinks": self.alarm.has_merged_downlinks(),
        }

    def set_item_status(self, alarm: ActiveAlarm, status: ItemStatus = ItemStatus.NEW):
        """
        Set status for Escalation Item

        Args:
            alarm: Alarm for item
            status: Status
        """
        for item in self.items:
            if str(item.alarm) == str(alarm.id) and status != ItemStatus.NEW:
                item.status = status
                break
            elif str(item.alarm) == str(alarm.id):
                break
        else:
            self.items += [
                Item(
                    alarm=alarm,
                    status=status,
                    # error ?
                )
            ]

    def get_lock_items(self) -> List[str]:
        s: Set[str] = set()
        # Add items
        for item in self.items:
            s.add(f"a:{item.alarm}")
        # Add references
        if self.groups:
            for group in self.groups:
                s.add(f"g:{group}")
        return list(s)

    def get_span_sample(self) -> int:
        """
        Calculate effective sample for escalation span
        """
        if self.alarm.managed_object.tt_system:
            return self.alarm.managed_object.tt_system.telemetry_sample
        return PARENT_SAMPLE

    def set_escalation_context(self):
        """Set escalation SPAN Id"""
        current_context, current_span = get_current_span()
        if current_context or self.ctx_id:
            self.ctx_id = current_context
            # self._get_collection().update_one(
            #     {"_id": self.id}, {"$set": {"ctx_id": current_context}}
            # )

    def get_status(self):
        """Calculate current Job status"""
        return self.status

    def run_once(
        self,
        actions: List[ActionReq],
        timestamp: Optional[datetime.datetime] = None,
        user: Optional[User] = None,
        tt_system: Optional[TTSystem] = None,
    ):
        """Run Action from request"""
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        logs = []
        for aa in actions:
            aa = ActionLog.from_request(
                aa,
                started_at=timestamp,
                one_time=True,
                user=user.id if user else None,
                tt_system=tt_system.id if tt_system else None,
            )
            logs.append(aa)
        self.run(logs)

    def add_action(self, a: ActionLog):
        """Add action to list"""
        # Sorted
        self.actions.append(a)

    def get_state(self) -> Dict[str, Any]:
        """Return Job State"""
        r = {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "items": [ii.get_state() for ii in self.items],
            "actions": [a.get_state() for a in self.actions],
            "groups": [{"id": g.id, "reference": g.reference} for g in self.groups],
            "end_condition": self.end_condition,
            "maintenance_policy": self.maintenance_policy,
            "policy": self.policy.value,
            "max_repeat": self.max_repeat,
            "repeat_delay": self.repeat_delay,
            "ctx_id": self.ctx_id,
            "telemetry_sample": self.telemetry_sample,
            "tt_docs": self.tt_docs,
            "affected_services": self.affected_services,
            "severity": self.severity,
            "total_objects": self.total_objects,
            "total_services": self.total_services,
            "total_subscribers": self.total_subscribers,
            "expires": None,
        }
        return r

    @classmethod
    def from_request(cls, req: EscalationRequest, dry_run: bool = False) -> "AlarmAutomationJob":
        """Build Job from Request"""
        alarm = get_alarm(req.item.alarm)
        if not alarm:
            raise ValueError("Not Found alarm by id: %s", req.item.alarm)
        groups = []
        if req.item.service:
            groups += [GroupItem(id=str(req.item.service), reference=alarm.reference)]
        elif req.item.group:
            groups += [GroupItem(id=str(req.item.group), reference=alarm.reference)]
        job = AlarmAutomationJob(
            status=JobStatus.NEXT,
            items=[Item(alarm=alarm)],
            groups=groups,
            policy=req.policy,
            name=str(req),
            id=req.id,
            ctx_id=req.ctx,
            actions=[
                ActionLog.from_request(
                    a, started_at=req.start_at, user=req.user, tt_system=req.tt_system
                )
                for a in req.actions
            ],
            end_condition=req.end_condition,
            maintenance_policy=req.maintenance_policy,
            #
            max_repeat=req.max_repeats,
            repeat_delay=req.repeat_delay,
            dry_run=dry_run,
        )
        return job

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "AlarmAutomationJob":
        """Restore Job from state"""
        job = AlarmAutomationJob(
            id=state["_id"],
            name=state["name"],
            status=JobStatus(state["status"]),
            items=[],
            actions=[ActionLog.from_dict(aa) for aa in state["actions"]],
            groups=[GroupItem(reference=gg["reference"], id=gg["id"]) for gg in state["groups"]],
            end_condition=state["end_condition"],
            maintenance_policy=state["maintenance_policy"],
            policy=EscalationGroupPolicy(state["policy"]),
            max_repeat=state["max_repeat"],
            repeat_delay=state["repeat_delay"],
            ctx_id=state["ctx_id"],
            telemetry_sample=state["telemetry_sample"],
            tt_docs=state.get("tt_docs"),
        )
        # Update docs
        return job

    def check_end(self) -> bool:
        """
        Check Escalation End Condition:
            * CR - Close Alarm Leader
            * CA - Close All alarm on escalation
            * CT - Close TT System Document (forced), supported get TT info
            * M - Manual Escalation Close (from alarm forced, set end_timestamp)
        """
        # if self.end_timestamp or self.alarm.status != "A":
        #    return True
        # Check if alarm leader was closed
        if self.end_condition == "CR":
            return self.leader_item.status == ItemStatus.REMOVED or self.alarm.status != "A"
        elif self.end_condition == "CA":
            return all(i.status == ItemStatus.REMOVED for i in self.items)
        # elif self.end_condition == "CT":
        # Close TT
        #    return self.alarm_log and self.escalations[0].deescalation_status == "ok"
        elif self.end_condition == "M" or self.end_condition == "CT":
            # Check Action, Action End - SuccessFul
            return bool(self.status == JobStatus.END)
        elif self.end_condition == "E":
            return self.actions[-1].status not in [ActionStatus.NEW, ActionStatus.PENDING]
        return False

    def iter_alarms_always_first(self) -> Iterable[ActiveAlarm]:
        """
        `always_first` escalation policy. Always escalate first alarm
        """
        if not self.groups:
            yield from self.iter_alarms_root()
            return
        for aa in ActiveAlarm.objects.filter(
            groups__in=[g.reference for g in self.groups]
        ).order_by("timestamp"):
            # if aa.managed_object.can_escalate():
            #     # Skip Disabled Escalation
            #     yield aa
            #     break
            yield aa
        # yield from self.alarm.iter_grouped()

    def iter_alarms_service(self) -> Iterable[ActiveAlarm]:
        """
        `root` escalation policy. If alarm is root cause, yield root alarm
        and all the consequences
        """
        if not self.groups:
            yield from self.iter_alarms_root()
            return
        for aa in ActiveAlarm.objects.filter(
            groups__in=[g.reference for g in self.groups],
        ).order_by("timestamp"):
            # if aa.managed_object.can_escalate():
            #     # Skip Disabled Escalation
            #     yield aa
            #     break
            yield aa

    def iter_alarms_root(self) -> Iterable[ActiveAlarm]:
        """
        `root` escalation policy. If alarm is root cause, yield root alarm
        and all the consequences
        """
        if self.alarm.root:
            self.logger.info("[root] Alarm is not a root cause. Skipping")
            return
        yield self.alarm
        yield from self.alarm.iter_consequences()

    def get_alarm_items(self) -> List[ActiveAlarm]:
        """"""
        match self.policy:
            case EscalationGroupPolicy.NEVER:
                return [self.alarm]
            case EscalationGroupPolicy.ROOT:
                return list(self.iter_alarms_root())
            case EscalationGroupPolicy.GROUP:
                return list(self.iter_alarms_always_first())
            case EscalationGroupPolicy.SERVICE:
                return list(self.iter_alarms_service())
        return [self.alarm]

    def update_items(self):
        """Update escalation doc items. Run on is_dirty"""

        def update_totals_from_summary(
            t_dict: DefaultDict[ObjectId, int], t_items: Iterable[SummaryItem]
        ) -> None:
            """
            Update totals from alarm summary
            """
            for item in t_items:
                t_dict[item.profile] += item.summary

        # Dynamic (save to field)
        # policy = self.policy.name.lower()
        # iter_items = getattr(self, f"iter_alarms_{policy}", None)
        # if not iter_items:
        #    self.logger.error("Unknown escalation policy `%s`. Skipping", policy)
        #    return None
        items = self.get_alarm_items()
        if not items:
            return None
        # Total counters
        total_objects: DefaultDict[int, int] = defaultdict(int)
        total_services: DefaultDict[ObjectId, int] = defaultdict(int)
        total_subscribers: DefaultDict[ObjectId, int] = defaultdict(int)
        # @todo: Append profile
        affected_services = set()
        if self.policy == EscalationGroupPolicy.SERVICE:
            affected_services.add(Service.get_by_id(self.groups[0].id))
        for alarm in items:
            if alarm.alarm_class.is_ephemeral:
                # Group alarms are virtual and should be locked, but not escalated
                # self.groups += [alarm.reference]
                continue
            if alarm.status == "C":
                self.set_item_status(alarm, ItemStatus.REMOVED)
                # Last_changed_set
            else:
                self.set_item_status(alarm, ItemStatus.NEW)
            # Update totals
            total_objects[alarm.managed_object.object_profile.id] += 1
            update_totals_from_summary(total_services, alarm.direct_services)
            update_totals_from_summary(total_subscribers, alarm.direct_subscribers)
            if alarm.affected_services:
                affected_services |= set(alarm.affected_services)

        # if not self.items:
        #    return None  # Only group alarms
        self.total_objects = [
            ObjectSummaryItem(profile=k, summary=v) for k, v in total_objects.items()
        ]
        self.total_services = [SummaryItem(profile=k, summary=v) for k, v in total_services.items()]
        self.total_subscribers = [
            SummaryItem(profile=k, summary=v) for k, v in total_subscribers.items()
        ]
        self.affected_services = list(affected_services)

    def get_tt_ids(self) -> str:
        """Return all escalated Document with TT system"""
        r = []
        for key, document_id in self.tt_docs.items():
            tt = TTSystem.get_by_id(key)
            r.append(f"{tt.name}:{document_id}")
        return ";".join(r)

    # Job API
    def is_blocked(self) -> bool:
        return not self.is_waiting

    @property
    def has_children(self) -> bool:
        return False

    # Status API
    @property
    def is_waiting(self) -> bool:
        return self.status == JobStatus.WAIT

    @property
    def is_running(self) -> bool:
        return self.status == JobStatus.PENDING

    @property
    def is_cancelled(self) -> bool:
        return self.status == JobStatus.CANCEL

    @property
    def is_complete_success(self) -> bool:
        return self.status in (
            JobStatus.END,
            JobStatus.WARNING,
        )

    @property
    def is_complete_failed(self) -> bool:
        return self.status in (
            JobStatus.FAILED,
            JobStatus.CANCEL,
        )

    @property
    def is_complete(self) -> bool:
        return self.status in (
            JobStatus.END,
            JobStatus.WARNING,
            JobStatus.FAILED,
            JobStatus.CANCEL,
        )
