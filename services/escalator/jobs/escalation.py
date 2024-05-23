# ---------------------------------------------------------------------
# Escalation Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from dataclasses import dataclass
from typing import Iterable, Dict, Optional, Any

# Third-party modules
import orjson
from bson import ObjectId
from pymongo import ReadPreference

# NOC modules
from noc.services.escalator.jobs.base import SequenceJob
from noc.core.span import Span, PARENT_SAMPLE
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.tt.types import EscalationItem as ECtxItem
from noc.core.tt.base import TTSystemCtx
from noc.core.perf import metrics
from noc.sa.models.action import Action
from noc.main.models.notificationgroup import NotificationGroup
from noc.fm.models.escalation import Escalation, ItemStatus, EscalationStatus
from noc.fm.models.escalationprofile import EscalationItem
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem


@dataclass
class EscalationResult(object):
    status: EscalationStatus = EscalationStatus.OK
    error: Optional[str] = None
    document: Optional[str] = None


class EscalationJob(SequenceJob):
    model = Escalation
    lock = ProcessLock(category="escalator", owner="escalator")

    def __init__(self, job, attrs):
        super().__init__(job, attrs)
        self.object = Escalation()
        self.alarm_log = []

    def run_action(self, action: str, key: str) -> EscalationResult:
        """
        Run Action API method
        """

    def can_escalate(self) -> bool:
        """
        Return True if alarm can be escalated.
        """
        if self.object.forced:
            return True
        return self.object.managed_object.can_escalate()

    def end_sequence(self):
        """
        Stop sequence
        """
        if self.alarm_log:
            coll = ActiveAlarm._get_collection()
            coll.bulk_write(self.alarm_log)
        self.object.save()

    def end_escalation(self, timestamp: Optional[datetime.datetime] = None):
        """
        Processed end escalation handlers
        ToDo:
            Check deescalation error before remove job
        """
        self.check_closed()
        if not self.object.end_timestamp:
            self.object.end_timestamp = datetime.datetime.now().replace(microsecond=0)
        self.end_sequence()

    def handler(self, **kwargs):
        self.logger.info("Performing escalations")
        if self.object.is_dirty:
            self.object.update_items()
            self.object.is_dirty = False
        # Check end escalation
        if self.object.check_end():
            self.end_escalation()
            if not self.error:
                self.remove_job()
            return
        # Check retry and waited escalations
        self.check_escalation_waited()
        # Check maintenances
        # Perform escalations
        with Span(
            client="escalator",
            sample=self.get_span_sample(),
            context=self.object.ctx_id,
        ) as span_ctx, self.lock.acquire(
            self.object.get_lock_items()
        ), change_tracker.bulk_changes():
            if not self.object.ctx_id:
                # span_ctx.span_context
                self.object.set_escalation_context()
            ctx = self.object.get_ctx()
            # Evaluate escalation chain
            for esc_item in self.iter_sequence():
                # Render TT subject and body
                subject = esc_item.template.render_subject(**ctx)
                body = esc_item.template.render_body(**ctx)
                # Escalate to TT
                if (
                    esc_item.create_tt
                    # check TT System items escalated
                    and self.can_escalate()
                    # and not self.is_already_escalated()
                    # and not self.is_under_maintenance()
                ):
                    tt_system = esc_item.tt_system or self.object.managed_object.tt_system
                    r = self.create_tt(tt_system, subject, body, ctx)
                    self.object.set_escalation(
                        action="tt_system",
                        key=str(tt_system),
                        status=r.status,
                        timestamp=datetime.datetime.now().replace(microsecond=0),
                        document_id=r.document,
                        error=r.error,
                    )
                    if r.status == EscalationStatus.OK:
                        self.notify_escalated_consequences(tt_system, r.document)
                    if r.status == EscalationStatus.TEMP:
                        self.set_temp_error(r.error)
                # Send notification
                if esc_item.notification_group:
                    r = self.notify(esc_item.notification_group, subject=subject, body=body)
                    # Save to escalation context
                    self.object.set_escalation(
                        timestamp=datetime.datetime.now().replace(microsecond=0),
                        action="notification",
                        key=str(esc_item.notification_group.id),
                        status=r.status,
                    )
                # Execute Diagnostic
                if esc_item.stop_processing:
                    self.logger.debug("Stopping processing")
                    break
        self.logger.info("Saving changes on: %s", self.object.sequence_num)
        self.end_sequence()

    def iter_sequence(self) -> Iterable[EscalationItem]:
        """
        Iterate over chain action with current step
        """

        ts = self.object.timestamp
        now = datetime.datetime.now().replace(microsecond=0)
        self.logger.info("Start escalation sequence from: %s", self.object.sequence_num)
        for num, item in enumerate(self.object.profile.escalations):
            if num < self.object.sequence_num:
                continue
            # Set current sequence
            self.object.sequence_num = num
            if (now - self.object.get_next(num)).total_seconds() < int(item.delay):
                break
            escalation = self.object.get_escalation(action=item.action, key=item.get_key())
            if escalation and escalation.status == EscalationStatus.OK:
                # Already escalated
                continue
            condition = True
            if item.alarm_ack == "ack" and not self.object.alarm.ack_ts:
                condition = False
            if item.alarm_ack == "nack" and self.object.alarm.ack_ts:
                condition = False
            # Check time pattern
            if item.time_pattern and not item.time_pattern.match(ts):
                condition = False
            if item.min_severity.severity and self.object.severity < item.min_severity.severity:
                condition = False
            if not condition:
                continue
            yield item
        self.logger.info("Escalation sequence is completed")
        if self.object.alarm == "A" and self.object.profile.close_alarm:
            # Clear Alarm after End
            self.close_alarm()
        if self.object.profile.end_condition == "E":
            # End if end condition
            self.end_escalation()
        # Remove or Suspend
        if not self.error:
            self.remove_job()

    def check_escalation_waited(self):
        """
        Retry escalation waited and temp error
        :return:
        """
        for item in self.object.escalations:
            if item.status != EscalationStatus.TEMP:
                continue
            # retry action

    def check_closed(self, reason: Optional[str] = None):
        """
        Close escalations
        """
        self.logger.info("Escalation ended and will by closed. Try to deescalate")
        for item in self.object.escalations:
            if (
                item.status != EscalationStatus.OK
                or item.deescalation_status == EscalationStatus.FAIL
            ):
                continue
            if item.deescalation_status and item.deescalation_status in (
                EscalationStatus.OK or EscalationStatus.FAIL
            ):
                continue
            if item.action == "tt_system" and item.document_id:
                tt = TTSystem.get_by_id(item.key)
                r = self.close_tt(tt, item.document_id)
            elif item.action == "notification":
                ng = NotificationGroup.get_by_id(int(item.key))
                r = self.notify(ng, "Alarm Closed")
            else:
                continue
            item.deescalation_status = r.status
            item.deescalation_error = r.error
            if r.status == EscalationStatus.TEMP:
                self.set_temp_error(r.error)

    def get_span_sample(self, tt_system: Optional[TTSystem] = None) -> int:
        """
        Calculate effective sample for escalation span

        Args:
            tt_system: TTSystem Instance
        """
        if tt_system:
            return tt_system.telemetry_sample
        return self.object.profile.telemetry_sample

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

    # TT System API
    def get_tt_system_context(self, tt_system: TTSystem) -> TTSystemCtx:
        cfg = self.object.profile.get_tt_system_config(tt_system)
        ctx = TTSystemCtx(
            tt_system=tt_system.get_system(),
            queue=self.object.managed_object.tt_queue,
            reason=cfg.get("pre_reason"),
            login=cfg.get("login"),
            timestamp=self.object.timestamp,
            is_unavailable=False,
        )
        return ctx

    def check_escalated(self):
        """
        Process escalation doc and fill already escalated alarms.
        Note: Must be called under the lock
        """
        alarms = [item.alarm for item in self.escalation_doc.items]
        esc_status: Dict[ObjectId, ObjectId] = {}
        esc_tt: Dict[ObjectId, str] = {}
        for doc in Escalation._get_collection().aggregate(
            [
                {
                    "$match": {
                        "end_timestamp": {"$exists": False},
                        "items.alarm": {"$in": alarms},
                        "escalations.document_id": {"$exists": True},
                    }
                },
                {"$project": {"_id": 1, "items": 1, "escalations": 1}},
                {"$unwind": "$items"},
                {"$match": {"items.alarm": {"$in": alarms}}},
            ]
        ):
            esc_status[doc["items"]["alarm"]] = doc["_id"]
            # esc_tt[doc["items"]["alarm"]] = doc.get("escalations", doc["items"].get("current_tt_id"))
        if not esc_status:
            return  # No escalated docs
        for item in self.object.items:
            if item.alarm in esc_status and item.is_new:
                self.logger.info(
                    "Alarm %s is already escalated with TT %s", item.alarm, esc_tt[item.alarm]
                )
                item.escalation_status = ItemStatus.EXISTS
                # item.current_escalation = esc_status[item.alarm]
                # item.current_tt_id = esc_tt[item.alarm]

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: str,
        body: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> EscalationResult:
        """
        Create Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body
            context: Escalation Context

        Returns:
            EscalationResult:
        """
        self.logger.debug("Escalation message:\nSubject: %s\n%s", subject, body)
        # Build Items for context
        self.check_escalated()
        e_ctx_items = [
            ECtxItem(
                id=str(self.object.managed_object.id), tt_id=self.object.managed_object.tt_system_id
            )
        ]
        for item in self.object.items[1:]:
            if item.is_already_escalated:
                continue
            if not item.managed_object.can_escalate(True):
                err = f"Cannot append object {item.managed_object.name} to group tt: Escalations are disabled"
                self.log_alarm(err)
                item.escalation_status = ItemStatus.FAIL
                continue
            if item.managed_object.tt_system != tt_system:
                err = f"Cannot append object {item.managed_object.name} to group tt: Belongs to other TT system"
                self.log_alarm(err)
                item.escalation_status = ItemStatus.FAIL
                continue
            ei = ECtxItem(id=str(item.managed_object.id), tt_id=item.managed_object.tt_system_id)
            e_ctx_items.append(ei)
        self.logger.info("Creating TT in system %s", tt_system.name)
        self.log_alarm(f"Creating TT in system {tt_system.name}")
        with self.get_tt_system_context(tt_system) as ctx:
            ctx.add_items(e_ctx_items)
            doc_id = ctx.create(subject=subject, body=body, data=context)
            if not doc_id and ctx.error_code:
                self.log_alarm(f"Failed to escalate: {ctx.error_text}")
                return EscalationResult(EscalationStatus(ctx.error_code, ctx.error_text))
            elif not doc_id:
                return EscalationResult(EscalationStatus.FAIL)
            # Project result to escalation items
            ctx_map: Dict[int:ItemStatus] = {}
            for item in ctx.items:
                try:
                    e_status = item.get_status()
                except AttributeError:
                    self.log_alarm(f"Adapter malfunction. Status for {item.id} is not set.")
                    continue
                if e_status.is_ok:
                    self.log_alarm(f"{item.id} is appended successfully")
                    e_status = ItemStatus.CHANGED
                else:
                    self.log_alarm(
                        f"Failed to append {item.id}: {e_status.msg} ({e_status.status})"
                    )
                    e_status = ItemStatus.FAIL
                ctx_map[item.id] = e_status
            for item in self.object.items:
                if item.managed_object.id not in ctx_map:
                    continue
                item.status = ctx_map[item.managed_object.id]
            metrics["escalation_tt_create"] += 1
        return EscalationResult(document=doc_id)

    def close_tt(
        self, tt_system: TTSystem, tt_id: str, reason: Optional[str] = None
    ) -> EscalationResult:
        """
        Close Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            reason: comment message for close reason

        Returns:
            Escalation Resul instance
        """
        self.logger.info("Closing TT %s:%s", tt_system, tt_id)
        with self.get_tt_system_context(tt_system) as ctx:
            ctx.close(tt_id)
            if ctx.error_code:
                metrics[f"escalation_tt_comment_fail"] += 1
                status = EscalationStatus(ctx.error_code)
                if status == EscalationStatus.TEMP:
                    error = f"Temporary error detected while closing tt {tt_id}: {ctx.error_text}"
                elif status == EscalationStatus.FAIL:
                    error = f"Failed to close tt {tt_id}: {ctx.error_text}"
                self.logger.info(error)
                return EscalationResult(status, error=error)
        return EscalationResult()

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
        with self.get_tt_system_context(tt_system) as ctx:
            ctx.comment(tt_id, message)
            metrics["escalation_tt_comment"] += 1
            if ctx.error_code:
                metrics[f"escalation_tt_comment_fail"] += 1
                return EscalationResult(
                    EscalationStatus(ctx.error_code),
                    error=f"Failed to add comment to {tt_id}: {ctx.error_text}",
                )
        return EscalationResult()

    def notify(
        self, notification_group, subject: str, body: Optional[str] = None
    ) -> EscalationResult:
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
        return EscalationResult()

    def action(self, action: Action) -> EscalationResult:
        """
        Run action for ManagedObject

        Todo:
            * for run script moved it to Action

        Args:
            action: Action Instance

        Returns:
            EscalationResult: Action data collected
        """

    def notify_escalated_consequences(self, tt_system, tt_id: str) -> None:
        """
        Append comments to all escalated consequences

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
        """

    def close_alarm(self):
        """
        Close Alarm
        """

    def alarm_ack(self, tt_system: Optional[TTSystem]):
        """
        Acknowledge alarm by tt_system or settings

        """
