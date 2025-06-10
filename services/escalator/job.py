# ----------------------------------------------------------------------
# Automation with processed alarm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import operator
import enum
import time
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Set, Iterable, Optional, Tuple, Dict, Any, DefaultDict

# Third-party modules
from bson import ObjectId


# NOC modules
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.span import Span
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.log import PrefixLoggerAdapter
from noc.core.perf import metrics
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    EscalationMember,
    TTActionContext,
    TTAction,
    EscalationGroupPolicy,
    EscalationRequest,
    Action as ActionReq,
)
from noc.core.tt.base import TTSystemCtx

# from noc.core.models.escalationpolicy import EscalationPolicy
from noc.core.timepattern import TimePattern
from noc.aaa.models.user import User
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.main.models.remotesystem import RemoteSystem
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.serviceprofile import ServiceProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from noc.maintenance.models.maintenance import Maintenance


class ActionStatus(enum.Enum):
    """
    Action Result Status

    Attributes:
        NEW: new action
        SUCCESS: run success
        FAILED: Failed with error
        WARNING: Warning. Failed, but allowed to fail.
        SKIP: Not running about condition
        PENDING: Pending, waiting for manual approve.
        CANCELLED: Cancelled, not repeat for run / OR Condition
    """

    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "w"
    # CANCELLED = "c"
    SKIP = "k"
    PENDING = "p"
    # WAIT_END = "we"
    # STOP = "stop/break"


class JobStatus(enum.Enum):
    """
    Job status.

    Attributes:
        PENDING: waiting for manual approve.
        NEXT:
        RUNNING:
        CANCEL: Job cancelled fot run
        WAIT: Waiting, ready to run.
        FAILED: End with fail
        WARNING: Failed, but allowed to fail.
        END: End job
        EXCEPTION: End for exception
    """

    PENDING = "p"  # Wait manual approve
    NEXT = "n"  # Next action
    WAIT = "w"  # Wait timestamp
    FAILED = "f"  # end with fail
    WARNING = "w"  # Retry errors
    CANCEL = "c"  # Manually cancelled
    END = "e"  # Run End
    EXCEPTION = "x"


class ItemStatus(enum.Enum):
    """
    Attributes:
        NEW: New items
        CHANGED: Items was changed
        FAIL: Failed when add to escalation
        EXISTS: Escalate over another doc
        REMOVED: Removed from escalation
    """

    NEW = "new"  # new item
    CHANGED = "changed"  # item changed
    FAIL = "fail"  # escalation fail
    EXISTS = "exists"  # Exists on another escalation
    REMOVED = "removed"  # item removed


@dataclass
class GroupItem(object):
    reference: bytes
    id: Optional[str] = None


@dataclass
class Item(object):
    """Over Job Item"""

    #! Replace to alarm List, status
    alarm: ActiveAlarm
    status: ItemStatus = ItemStatus.NEW

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return self.alarm.managed_object


@dataclass(frozen=True)
class ActionResult(object):
    """
    Action result class
    Attributes:
        status: Action Status Result
        error: Error message
        document_id: Id on remote system\
        ctx: Action context data
    """

    status: ActionStatus
    error: Optional[str] = None
    document_id: Optional[str] = None
    ctx: Optional[Dict[str, str]] = None


class ActionLog(object):
    """Action Part of log with Run"""

    def __init__(
        self,
        action: TTAction,
        key,
        # Match
        time_pattern: Optional[TimePattern] = None,
        min_severity: Optional[int] = None,
        # Time ?
        delay: int = 0,
        timestamp: Optional[datetime.datetime] = None,
        status: ActionStatus = ActionStatus.NEW,
        error: Optional[str] = None,
        # Stop processed after action
        stop_processing: bool = False,
        # Source Task
        user: Optional[User] = None,
        tt_system: Optional[TTSystem] = None,
        document_id: Optional[str] = None,
        template: Optional[str] = None,
        **kwargs,
    ):
        self.action = action
        self.key = key
        # To ctx ?
        self.template: Optional[Template] = Template.get_by_id(int(template)) if template else None
        self.timestamp = timestamp  # run_at
        self.status = status
        self.error = error
        self.document_id = document_id
        self.min_severity = min_severity
        self.time_pattern: Optional[TimePattern] = time_pattern
        self.stop_processing = stop_processing
        self.repeat_num = 0
        self.ctx = kwargs

    def __str__(self):
        return f"{self.action} ({self.key}): {self.status} ({self.timestamp})"

    def set_status(self, result: ActionResult):
        """Update Action Log"""
        self.status = result.status
        self.error = result.error
        if result.ctx:
            self.ctx |= result.ctx

    def is_match(self, severity: int, timestamp: datetime.datetime):
        """Check job condition"""
        if severity < self.min_severity:
            return False
        elif self.time_pattern and not self.time_pattern.match(timestamp):
            return False
        return True

    def to_run(self, status: JobStatus, delay: int):
        """
        Check job allowed to run
        next -> new + check delay
        repeat -> new
        retry -> temp_failed
        failed -> -
        Return -> stop(check stop processing)/run/skip(next)
        """
        if status == status.NEXT and self.status == ActionStatus.NEW:
            return True
        elif status == status.WARNING and self.status == ActionStatus.WARNING:
            return True
        return False

    def get_ctx(self, item_ctx: Dict[str, Any], docs_ids: Dict[str, str]) -> Dict[str, Any]:
        """Build action CTX"""
        r = {"timestamp": self.timestamp}
        if self.action == TTAction.CREATE_TT or self.action == TTAction.CLOSE_TT:
            r["tt_system"] = TTSystem.get_by_id(self.key)
            r["tt_id"] = docs_ids.get(self.key)
        elif self.action == TTAction.NOTIFY:
            r["notification_group"] = NotificationGroup.get_by_id(int(self.key))
        if self.template:
            r["subject"] = self.template.render_subject(**item_ctx)
            r["body"] = self.template.render_body(**item_ctx)
        if self.ctx:
            r |= self.ctx
        return r

    def get_repeat(self, delay: int) -> "ActionLog":
        """Return repeated Action"""
        return ActionLog(
            action=self.action,
            key=self.key,
            status=ActionStatus.NEW,
            timestamp=self.timestamp + datetime.timedelta(seconds=delay),
            # @todo
            repeat_num=self.repeat_num + 1,
        )

    @classmethod
    def from_request(cls, action: ActionReq, started_at: datetime.datetime) -> "ActionLog":
        """"""
        return ActionLog(
            action=action.action,
            key=action.key,
            template=action.template,
            timestamp=started_at + datetime.timedelta(seconds=action.delay),
            time_pattern=action.time_pattern,
            min_severity=action.min_severity or 0,
            stop_processing=action.stop_processing,
            login=action.login,
        )


class AlarmAutomationJob(object):
    """
    Runtime Alarm Automation
    """

    lock = ProcessLock(category="escalator", owner="escalator")

    def __init__(
        self,
        name: str,
        status: JobStatus,
        items: List[Item],
        # alarms_ids
        actions: List[ActionLog],
        groups: Optional[List[GroupItem]] = None,
        end_condition: str = "CR",
        # items_policy: EscalationPolicy = EscalationPolicy.ROOT,
        policy: EscalationGroupPolicy = EscalationGroupPolicy.ROOT,
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        id: Optional[str] = None,
        allow_fail: bool = False,
        logger: Optional[Any] = None,
        dry_run: bool = False,
    ):
        self.id = id
        self.name = name
        self.status = status
        self.items = items
        self.groups: List[GroupItem] = groups or []
        self.actions = actions
        self.ctx_id = ctx_id
        self.telemetry_sample = telemetry_sample
        self.allow_fail = allow_fail
        # self.items_policy = items_policy
        self.policy = policy or EscalationGroupPolicy.ROOT
        self.end_condition = end_condition or "CR"
        self.dry_run = dry_run
        self.tt_docs: Dict[str, str] = {}  # TTSystem -> doc_id
        self.alarm_log = []
        self.end_at: Optional[datetime.datetime] = None
        self.max_repeat = 0
        self.repeat_delay = 60
        self.affected_services = []
        # Alarm Severity
        self.severity = 0
        self.total_objects = []
        self.total_services = []
        self.total_subscribers = []
        self.logger = logger or PrefixLoggerAdapter(
            logging.getLogger(__name__), f"[{self.id}|{self.leader.alarm}"
        )

    @property
    def leader(self) -> "Item":
        """Return first item"""
        return self.items[0]

    @property
    def alarm(self) -> ActiveAlarm:
        """Getting document alarm"""
        return self.leader.alarm

    def set_item_status(
        self,
        alarm: ActiveAlarm,
        status: ItemStatus = ItemStatus.NEW,
        error: Optional[str] = None,
    ):
        """
        Set status for Escalation Item

        Args:
            alarm: Alarm for item
            status: Status
            error: Error text for Status
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
                    # managed_object_id=alarm.managed_object.id,
                    # target_reference=
                    alarm=alarm,
                    status=status,
                )
            ]

    def run(self):
        """
        Run Job
        Iterate over jobs, and run it
        Repeating Job
        Returb Job status and Next timestamp
        """
        status = self.get_status()
        is_end = self.check_end()
        ts = datetime.datetime.now()
        actions = []
        self.logger.info("Processed actions from : %s", ts)
        self.update_items()
        print("ITEMS", self.items, self.affected_services)
        # with (
        #     Span(
        #         client="escalator",
        #         sample=self.get_span_sample(),
        #         context=self.ctx_id,
        #     ),
        #     self.lock.acquire(self.get_lock_items()),
        #     change_tracker.bulk_changes(),
        # ):
        #     if not self.object.ctx_id:
        #         # span_ctx.span_context
        #         self.set_escalation_context()
        ctx = self.get_ctx()
        # Sorted by ts
        for aa in sorted(self.actions, key=operator.attrgetter("timestamp")):
            self.logger.info("[%s] Processed action", aa)
            if aa.status in [ActionStatus.SUCCESS, ActionStatus.FAILED]:
                # Skip already running job
                continue
            elif not aa.is_match(self.severity, ts):
                # Set Skip (Condition)
                continue
            elif self.dry_run:
                wait_interval = (ts - aa.timestamp).total_seconds()
                self.logger.info("Dry run mode, waiting interval: %s", wait_interval)
                # time.sleep(abs(wait_interval) + 1)
                time.sleep(10)
            elif aa.timestamp > ts:
                break
            # if not aa.to_run(status, delay):
            #    continue
            try:
                r = self.run_action(
                    aa.action, **aa.get_ctx(ctx, docs_ids=self.tt_docs)
                )  # aa.get_ctx for job
            except Exception as e:
                r = ActionResult(status=ActionStatus.FAILED, error=str(e))  # Exception Status
                # Job Status to Exception
            self.logger.info("[%s] Action result: %s", aa, r)
            if aa.repeat_num < self.max_repeat and r.status == ActionStatus.SUCCESS:
                # If Repeat - add action to next on repeat delay
                # Self register actions
                actions.append(aa.get_repeat(self.repeat_delay))
            aa.set_status(r)
            if r.document_id:
                self.tt_docs[aa.key] = r.document_id
            # Processed Result
            if aa.stop_processing:
                # Set Stop job status
                break

    def get_status(self):
        """Calculate current Job status"""
        return self.status

    def get_delay(self) -> int:
        """Calculate current job delay"""

    def run_once(
        self,
        actions: List[ActionReq],
        user: Optional[User] = None,
        tt_system: Optional[TTSystem] = None,
    ):
        """Run Action from request"""

    def add_action(self, req: ActionReq, result: Optional[ActionResult] = None):
        """Add action to list"""

    def run_action(
        self,
        action: TTAction,
        **ctx: Dict[str, str],
    ) -> ActionResult:
        """Execute action"""
        match action:
            case TTAction.CREATE_TT:
                r = self.create_tt(**ctx)
            case TTAction.CLOSE_TT:
                r = self.close_tt(**ctx)
            case TTAction.CLEAR:
                r = self.alarm_clear(**ctx)
            case TTAction.ACK:
                r = self.alarm_ack(**ctx)
            case TTAction.UN_ACK:
                r = self.alarm_unack(**ctx)
            case TTAction.NOTIFY:
                # alarm.log_message(change.message, source=str(user))
                r = self.notify(**ctx)
            case _:
                raise NotImplementedError("Action %s not implemented" % action)
        return r

    def get_state(self) -> Dict[str, Any]:
        """Return Job State"""

    @classmethod
    def from_request(cls, req: EscalationRequest, dry_run: bool = False) -> "AlarmAutomationJob":
        """Build Job from Request"""
        alarm = get_alarm(req.item.alarm)
        groups = []
        if req.item.service:
            groups += [GroupItem(id=str(req.item.service), reference=alarm.reference)]
        job = AlarmAutomationJob(
            status=JobStatus.NEXT,
            items=[Item(alarm=alarm)],
            name=str(req),
            ctx_id=req.ctx,
            actions=[ActionLog.from_request(a, started_at=req.timestamp) for a in req.actions],
            end_condition=req.end_condition,
            groups=groups,
            policy=req.policy,
            dry_run=dry_run,
        )
        return job

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "AlarmAutomationJob":
        """Restore Job from state"""
        job = AlarmAutomationJob(
            **state,
        )
        return job

    def log_alarm(self, message: str, *args) -> None:
        """
        Log message to alarm

        Args:
            message: message for add to log
        """
        msg = message % args
        self.logger.info("[%s] Log alarm: %s", self.alarm, msg)
        if self.alarm.status == "C":
            # For closed alarm
            self.alarm.log_message(msg)
            self.alarm.save()
        else:
            self.alarm.log_message(msg, bulk=self.alarm_log)

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
            return self.leader.status == ItemStatus.REMOVED
        elif self.end_condition == "CA":
            return all(i.status == ItemStatus.REMOVED for i in self.items)
        # elif self.end_condition == "CT":
        # Close TT
        #    return self.alarm_log and self.escalations[0].deescalation_status == "ok"
        elif self.end_condition == "M" or self.end_condition == "CT":
            return bool(self.end_at)
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

    def iter_alarms_items(self) -> List[ActiveAlarm]:
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
        items = self.iter_alarms_items()
        if not items:
            return None
        # Total counters
        total_objects: DefaultDict[int, int] = defaultdict(int)
        total_services: DefaultDict[ObjectId, int] = defaultdict(int)
        total_subscribers: DefaultDict[ObjectId, int] = defaultdict(int)
        # @todo: Append profile
        affected_services = set()
        for alarm in items:
            if alarm.alarm_class.is_ephemeral:
                # Group alarms are virtual and should be locked, but not escalated
                # self.groups += [alarm.reference]
                continue
            if alarm.status == "C":
                self.set_item_status(alarm, ItemStatus.REMOVED)
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

    def has_merged_downlinks(self):
        """
        Check if alarm has merged downlinks
        """
        return bool(
            ActiveAlarm.objects.filter(root=self.alarm.id, rca_type=RCA_DOWNLINK_MERGE).first()
        )

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
            "service": (
                None
                if self.policy != EscalationGroupPolicy.SERVICE
                else Service.get_by_id(self.groups[0].id)
            ),
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
            "has_merged_downlinks": self.has_merged_downlinks(),
        }

    def get_tt_ids(self) -> str:
        """Return all escalated Document with TT system"""
        r = []
        for key, document_id in self.tt_docs.items():
            tt = TTSystem.get_by_id(key)
            r.append(f"{tt.name}:{document_id}")
        return ";".join(r)

    def comment_tt(
        self,
        tt_system: TTSystem,
        tt_id: str,
        message: str,
        timestamp: Optional[datetime.datetime] = None,
        **kwargs,
    ) -> EscalationResult:
        """
        Append Comment to Trouble Ticket

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            message: comment message

        Returns:
            Escalation Resul instance
        """
        self.logger.info("Appending comment to TT %s:%s", tt_system, tt_id)
        with self.get_tt_system_context(tt_system, tt_id, timestamp) as ctx:
            ctx.comment(message)
        r = ctx.get_result()
        if r.is_ok:
            metrics["escalation_tt_comment"] += 1
            return r
        if r.status == EscalationStatus.TEMP:
            metrics["escalation_tt_comment_fail"] += 1
            error = f"Failed to add comment to {tt_id}: {r.error}"
        elif r.status == EscalationStatus.FAIL:
            metrics["escalation_tt_comment_fail"] += 1
            error = f"Failed to close tt {tt_id}: {ctx.error_text}"
        else:
            error = r.error
        self.logger.info(error)
        return r

    def notify(
        self, notification_group, subject: str, body: Optional[str] = None, **kwargs
    ) -> ActionResult:
        """
        Send Notification

        Args:
            notification_group: Notification Group Instance
            subject: Message Subject
            body: Message Body

        Returns:
            EscalationResult: Escalation Resul instance
        """
        self.logger.info(
            "[%s] Notification message:\nSubject: %s\n%s", notification_group, subject, body
        )
        self.log_alarm(f"Sending notification to group {notification_group.name}")
        notification_group.notify(subject, body)
        metrics["escalation_notify"] += 1
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_ack(
        self, tt_system: Optional[TTSystem], user: User, message: Optional[str] = None, **kwargs
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        message = message or f"Acknowledge by TTSystem: {tt_system.name}"
        self.alarm.acknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_unack(
        self,
        tt_system: Optional[TTSystem],
        user: User,
        message: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        **kwargs,
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        message = message or f"UnAcknowledge by TTSystem: {tt_system.name}"
        self.alarm.unacknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_clear(
        self,
        tt_system: Optional[TTSystem],
        user: User,
        message: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        **kwargs,
    ):
        """
        Clear alarm by tt_system or settings

        """
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        self.alarm.register_clear(
            f"Clear by TTSystem: {tt_system.name}",
            user=user,
            timestamp=timestamp,
        )
        # Delayed, checked action - status return other service
        return ActionResult(status=ActionStatus.SUCCESS)

    def get_escalation_items(self, tt_system: TTSystem) -> List[ECtxItem]:
        """
        Build escalation items for Escalation Doc
        Args:
            tt_system: TTSystem for checked item

        """
        r = []
        rs = RemoteSystem.get_by_name("CMDB")
        for item in self.items:
            # if item.is_already_escalated:
            #     continue
            rid = item.managed_object.get_mapping(rs)
            if rid:
                r.append(
                    ECtxItem(id=str(item.managed_object.id), tt_id=rid),
                )
                continue
            if not item.managed_object.can_escalate(True):
                err = f"Cannot append object {item.managed_object.name} to group tt: Escalations are disabled"
                self.log_alarm(err)
                item.escalation_status = "fail"
                continue
            if item.managed_object.tt_system != tt_system:
                err = f"Cannot append object {item.managed_object.name} to group tt: Belongs to other TT system"
                self.log_alarm(err)
                item.escalation_status = "fail"
                continue
            ei = ECtxItem(id=str(item.managed_object.id), tt_id=item.managed_object.tt_system_id)
            r.append(ei)
        return r

    def get_affected_services_items(self) -> List[EscalationServiceItem]:
        """Return Affected Service item for escalation doc"""
        if self.policy == EscalationGroupPolicy.SERVICE:
            svc = Service.get_by_id(self.groups[0].id)
            return [
                EscalationServiceItem(
                    id=str(svc.id),
                    tt_id=svc.remote_id or "",
                )
            ]
        elif not self.affected_services:
            return []
        r = []
        for svc in Service.objects.filter(id__in=self.affected_services):
            r.append(
                EscalationServiceItem(
                    id=str(svc.id),
                    tt_id=svc.remote_id or "",
                )
            )
        return r

    def get_tt_system_context(
        self,
        tt_system: TTSystem,
        tt_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
    ) -> TTSystemCtx:
        """
        Build TTSystem Context
        Args:
            tt_system: TTSystem instance
            tt_id: Document ID
            timestamp:
            login:

        """
        # cfg = self.get_tt_system_config(tt_system)
        cfg = tt_system.get_config()
        # actions = self.get_action_context()
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=self.leader.managed_object.tt_queue,
            reason=None,
            login=login or cfg.login,
            timestamp=timestamp,
            actions=[],
            items=self.get_escalation_items(tt_system) if cfg.promote_item else [],
            services=self.get_affected_services_items() or None,
        )
        return ctx

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: str,
        body: str,
        context: Optional[Dict[str, Any]] = None,
        tt_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        **kwargs,
    ) -> ActionResult:
        """
        Create Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body
            context: Escalation Context
            tt_id: If set, do changes

        Returns:
            EscalationResult:
        """
        self.logger.debug(
            "Escalation message:\nSubject: %s\n%s",
            subject,
            body,
        )
        # Build Items for context
        # self.check_escalated()
        if tt_id:
            self.logger.info("Changed TT in system %s:%s", tt_system.name, tt_id)
            self.log_alarm(f"Changed TT in system {tt_system.name}")
        else:
            self.logger.info("Creating TT in system %s (%s)", tt_system.name, login)
            self.log_alarm(f"Creating TT in system {tt_system.name}")
        with self.get_tt_system_context(tt_system, tt_id, timestamp, login) as ctx:
            ctx.create(subject=subject, body=body)
        r = ctx.get_result()
        if r.status == EscalationStatus.TEMP:
            metrics["escalation_tt_retry"] += 1
            tt_system.register_failure()
            return ActionResult(status=ActionStatus.WARNING, error=r.error)
        elif r.status == EscalationStatus.FAIL or not r.is_ok or not r.document:
            self.log_alarm(f"Failed to create TT: {r.error}")
            metrics["escalation_tt_fail"] += 1
            # self.object.alarm.log_message(f"Failed to escalate: {r.error}")
            return ActionResult(status=ActionStatus.FAILED, error=r.error)
        if r.document:
            return ActionResult(status=ActionStatus.SUCCESS, document_id=r.document)
        # @todo r.document != tt_id
        # Project result to escalation items
        ctx_map = {}
        for item in ctx.items:
            try:
                e_status = item.get_status()
            except AttributeError:
                self.log_alarm(f"Adapter malfunction. Status for {item.id} is not set.")
                continue
            if e_status == EscalationStatus.OK:
                self.log_alarm(f"{item.id} is appended successfully")
                e_status = "changed"
            else:
                self.log_alarm(f"Failed to append {item.id}: {item._message} ({e_status})")
                e_status = "fail"
            ctx_map[item.id] = e_status
        for item in self.items:
            if item.managed_object.id not in ctx_map:
                continue
            item.status = ctx_map[item.managed_object.id]
        metrics["escalation_tt_create"] += 1
        return ActionResult(status=ActionStatus.SUCCESS, document_id=tt_id)

    def close_tt(
        self,
        tt_system: TTSystem,
        tt_id: str,
        reason: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        **kwargs,
    ) -> ActionResult:
        """
        Close Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            reason: comment message for close reason
            timestamp:

        Returns:
            Escalation Resul instance
        """
        if not tt_id:
            return ActionResult(status=ActionStatus.SKIP)
        self.logger.info("Closing TT %s:%s", tt_system, tt_id)
        with self.get_tt_system_context(tt_system, tt_id, timestamp, login) as ctx:
            ctx.close()
        r = ctx.get_result()
        if r.is_ok:
            metrics["escalation_tt_close"] += 1
            return ActionResult(status=ActionStatus.SUCCESS)
        if r.status == EscalationStatus.TEMP:
            metrics["escalation_tt_close_retry"] += 1
            tt_system.register_failure()
            # To Up on Job
            error = f"Temporary error detected while closing tt {tt_id}: {r.error}"
        elif r.status == EscalationStatus.FAIL:
            metrics["escalation_tt_close_fail"] += 1
            error = f"Failed to close tt {tt_id}: {ctx.error_text}"
        else:
            error = r.error
        self.logger.info(error)
        return ActionResult(status=ActionStatus.FAILED, error=error)
