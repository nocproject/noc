# ----------------------------------------------------------------------
# Automation with processed alarm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
import datetime

# Python modules
import logging
import enum
from dataclasses import dataclass
from typing import List, Set, Iterable, Optional, Tuple, Dict, Any

# Third-party modules
from bson import ObjectId


# NOC modules
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.perf import metrics
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    EscalationMember,
    TTActionContext,
    TTAction,
    EscalationRequest,
    Action as ActionReq,
)
from noc.core.tt.base import TTSystemCtx
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm


class ActionStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
    """

    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"
    SKIP = "s"
    WAIT_END = "we"
    STOP = "stop/break"


class JobStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `r` - Running
        * `S` - Suspended
        * `s` - Success
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
        * `c` - Cancelled
    """

    PENDING = "p"  # Wait manual approve
    NEXT = "n"  # Next action
    WAIT = "w"  # Wait timestamp
    FAILED = "f"  # end with fail
    WARNING = "w"  # Retry errors
    CANCEL = "c"  # Manually cancelled
    END = "e"  # Run End


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
class Item(object):
    """Over Job Item"""

    managed_object_id: int
    alarm: ObjectId
    status: ItemStatus = ItemStatus.NEW


@dataclass(frozen=True)
class ActionResult(object):
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
        **kwargs,
    ):
        self.action = action
        self.key = key
        self.template: Template = None
        self.timestamp = timestamp
        self.status = status
        self.error = error
        self.ctx = kwargs
        self.document_id = document_id
        self.min_severity = 0
        self.stop_processing = stop_processing
        self.time_pattern = None

    def set_status(self, result: ActionResult):
        """Update Action Log"""

    def is_match(self, severity: int, timestamp):
        """Check job condition"""
        if severity > self.min_severity:
            return False
        elif self.timestamp and not self.timestamp.match(timestamp):
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

    def get_ctx(self) -> Dict[str, Any]:
        """Build action CTX"""
        r = {}
        if self.action == TTAction.CREATE:
            r["tt_system"] = TTSystem.get_by_id(self.key)
        elif self.action == TTAction.NOTIFY:
            r["notification_group"] = NotificationGroup.get_by_id(self.key)
        r["subject"] = self.template.render_subject(**e_ctx)
        r["body"] = self.template.render_body(**e_ctx)
        return r


class AlarmAutomationJob(object):
    """
    Runtime Alarm Automation
    """

    def __init__(
        self,
        name: str,
        status: JobStatus,
        items: List[Item],
        # alarms_ids
        actions: List[ActionLog],
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        id: Optional[str] = None,
        allow_fail: bool = False,
        logger: Optional[Any] = None,
        dry_run: bool = False,
    ):
        self.name = name
        self.status = status
        self.items = items
        self.actions = actions
        self.ctx_id = ctx_id
        self.telemetry_sample = telemetry_sample
        self.allow_fail = allow_fail
        self.logger = logger
        self.dry_run = dry_run
        self.tt_docs: Dict[str, str] = {}  # TTSystem -> doc_id
        self.alarm_log = []
        # Alarm Severity
        self.severity = 0

    def run(self):
        """Run Job"""
        status = self.get_status()
        is_end = False
        delay = 0
        ts = datetime.datetime.now()
        for aa in self.actions:
            #
            if not aa.is_match(self.severity, ts):
                continue
            if aa.stop_processing:
                # Set Stop job status
                break
            if aa.to_run(status, delay):
                self.run_action(aa.action, **aa.get_ctx())  # aa.get_ctx for job
            elif aa.to_run(status, delay) is None:
                # Stop processing ?Add stop action
                break
            # If Repeat - add action to next on repeat delay
            # Self register actions

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
            case TTAction.CREATE:
                self.create_tt(**ctx)
            case TTAction.CLOSE:
                alarm.register_clear(
                    f"Clear by TTSystem: {self.object.name}",
                    user=user,
                    timestamp=change.timestamp,
                )
            case TTAction.ACK:
                self.alarm_ack(**ctx)
            case TTAction.UN_ACK:
                self.alarm_unack(**ctx)
            case TTAction.NOTIFY:
                # alarm.log_message(change.message, source=str(user))
                self.notify(**ctx)

    def get_state(self) -> Dict[str, Any]:
        """Return Job State"""

    @classmethod
    def from_request(cls, req: EscalationRequest) -> "AlarmAutomationJob":
        """Build Job from Request"""
        job = AlarmAutomationJob(
            name=str(req),
            ctx_id=req.ctx,
        )
        return job

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "AlarmAutomationJob":
        """Restore Job from state"""
        job = AlarmAutomationJob()
        return job

    def log_alarm(self, message: str, *args) -> None:
        """
        Log message to alarm

        Args:
            message: message for add to log
        """
        msg = message % args
        self.logger.info("[%s] Log alarm: %s", self.object.alarm, msg)
        if self.object.alarm.status == "C":
            # For closed alarm
            self.object.alarm.log_message(msg)
            self.object.alarm.save()
        else:
            self.object.alarm.log_message(msg, bulk=self.alarm_log)

    def comment_tt(self, tt_system: TTSystem, tt_id: str, message: str) -> EscalationResult:
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
        with self.get_tt_system_context(tt_system, tt_id) as ctx:
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

    def notify(self, notification_group, subject: str, body: Optional[str] = None) -> ActionResult:
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

    def alarm_ack(self, tt_system: Optional[TTSystem], user: User, message: Optional[str] = None):
        """
        Acknowledge alarm by tt_system or settings

        """
        message = message or f"Acknowledge by TTSystem: {tt_system.name}"
        self.alarm.acknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_unack(self, tt_system: Optional[TTSystem], user: User, message: Optional[str] = None):
        """
        Acknowledge alarm by tt_system or settings

        """
        message = message or f"UnAcknowledge by TTSystem: {tt_system.name}"
        self.alarm.unacknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def get_tt_system_context(
        self, tt_system: TTSystem, tt_id: Optional[str] = None
    ) -> TTSystemCtx:
        """
        Build TTSystem Context
        Args:
            tt_system: TTSystem instance
            tt_id: Document ID

        """
        cfg = self.object.profile.get_tt_system_config(tt_system)
        actions = self.get_action_context()
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=self.object.managed_object.tt_queue,
            reason=None,
            login=cfg.login,
            timestamp=self.object.timestamp,
            actions=actions,
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
        self.check_escalated()
        if tt_id:
            self.logger.info("Changed TT in system %s:%s", tt_system.name, tt_id)
            self.log_alarm(f"Changed TT in system {tt_system.name}")
        else:
            self.logger.info("Creating TT in system %s", tt_system.name)
            self.log_alarm(f"Creating TT in system {tt_system.name}")
        with self.get_tt_system_context(tt_system, tt_id) as ctx:
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
        if tt_id:
            return ActionResult(status=ActionStatus.SUCCESS, document_id=tt_id)
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
        self, tt_system: TTSystem, tt_id: str, reason: Optional[str] = None
    ) -> ActionResult:
        """
        Close Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            reason: comment message for close reason

        Returns:
            Escalation Resul instance
        """
        if not tt_id:
            return ActionResult(status=ActionStatus.SKIP)
        self.logger.info("Closing TT %s:%s", tt_system, tt_id)
        with self.get_tt_system_context(tt_system, tt_id) as ctx:
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
