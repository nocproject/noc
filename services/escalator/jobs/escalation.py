# ---------------------------------------------------------------------
# Escalation Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from dataclasses import dataclass
from typing import Iterable, Dict, List, Optional, Any, Tuple

# Third-party modules
import orjson
from pymongo import ReadPreference

# NOC modules
from noc.services.escalator.jobs.base import SequenceJob
from noc.core.span import Span, PARENT_SAMPLE
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.tt.types import EscalationItem as ECtxItem
from noc.core.tt.base import TTSystemCtx
from noc.core.perf import metrics
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.action import Action
from noc.main.models.notificationgroup import NotificationGroup
from noc.fm.models.escalation import Escalation
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
                    r = self.create_tt(tt_system, subject, body)  # ctx
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

    def create_tt(self, tt_system: TTSystem, subject: str, body: str) -> EscalationResult:
        """
        Create Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body

        Returns:
            EscalationResult:
        """
        self.logger.debug("Escalation message:\nSubject: %s\n%s", subject, body)
        self.logger.info("Creating TT in system %s", tt_system)
        return EscalationResult(document="example")

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
