# ---------------------------------------------------------------------
# Escalation Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Iterable, Dict, Optional, Any, List

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.services.escalator.jobs.base import SequenceJob
from noc.core.span import Span
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationStatus,
    EscalationResult,
    EscalationMember,
    TTActionContext,
    TTAction,
)
from noc.core.tt.base import TTSystemCtx
from noc.core.perf import metrics
from noc.sa.models.action import Action
from noc.main.models.notificationgroup import NotificationGroup
from noc.fm.models.escalation import Escalation, ItemStatus
from noc.fm.models.escalationprofile import EscalationItem
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem


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
        # return self.object.managed_object.can_escalate()
        return True

    def end_sequence(self):
        """
        Stop sequence
        """
        self.logger.info("Escalation sequence is completed")
        if (
            self.object.profile.repeat_escalations == "D"
            and self.object.profile.max_repeats < self.object.get_repeat()
        ):
            self.object.sequence_num = 0
            return
        elif self.object.alarm == "A" and self.object.profile.close_alarm:
            # Clear Alarm after End
            self.object.alarm.register_clear("Cleared by End Escalation Sequence")
        elif self.object.profile.end_condition == "E":
            # End if end condition
            self.end_escalation()
            return
        self.remove_job()

    def end_escalation(self, timestamp: Optional[datetime.datetime] = None):
        """
        Processed end escalation handlers
        """
        self.check_closed()
        if not self.object.end_timestamp:
            self.object.end_timestamp = datetime.datetime.now().replace(microsecond=0)
        # Remove or Suspend
        if not self.error:
            self.remove_job()

    def handler(self, **kwargs):
        self.logger.info("Performing escalations")
        changes = self.object.is_dirty
        if self.object.is_dirty:
            self.object.update_items()
            self.object.is_dirty = False
        # Check end escalation
        if self.object.check_end():
            self.end_escalation()
            if not self.error:
                self.remove_job()
            return
        # Check maintenances
        # Perform escalations
        with (
            Span(
                client="escalator",
                sample=self.get_span_sample(),
                context=self.object.ctx_id,
            ) as span_ctx,
            self.lock.acquire(self.object.get_lock_items()),
            change_tracker.bulk_changes(),
        ):
            if not self.object.ctx_id:
                # span_ctx.span_context
                self.object.set_escalation_context()
            ctx = self.object.get_ctx()
            # Check retry and waited escalations
            if self.object.sequence_num:
                self.check_escalation_waited(ctx, changes)
            # Evaluate escalation chain
            for esc_item in self.iter_sequence():
                if not esc_item.template:
                    self.logger.info("No escalation template, skipping")
                    self.log_alarm("No escalation template, skipping")
                    continue
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
                    if not tt_system:
                        continue
                    r = self.create_tt(tt_system, subject, body, ctx)
                    self.object.set_escalation(
                        member=EscalationMember.TT_SYSTEM,
                        key=str(tt_system.id),
                        status=r.status,
                        timestamp=datetime.datetime.now().replace(microsecond=0),
                        document_id=r.document,
                        error=r.error,
                        template=str(esc_item.template.id),
                    )
                    if r.status == EscalationStatus.OK:
                        self.notify_escalated_consequences(tt_system, r.document)
                    elif r.status == EscalationStatus.TEMP:
                        self.set_temp_error(r.error)
                    elif r.status == EscalationStatus.WAIT:
                        # Run wait Jobs and add document to waiting status
                        # 1. Get document status
                        # 2. Run Action: close alarm, Ack Alarm, Run Action
                        pass
                # Send notification
                if esc_item.notification_group:
                    r = self.notify(esc_item.notification_group, subject=subject, body=body)
                    # Save to escalation context
                    self.object.set_escalation(
                        timestamp=datetime.datetime.now().replace(microsecond=0),
                        member=EscalationMember.NOTIFICATION_GROUP,
                        key=str(esc_item.notification_group.id),
                        status=r.status,
                        template=str(esc_item.template.id),
                    )
        self.logger.info("Saving changes on: %s", self.object.sequence_num)
        if self.alarm_log:
            coll = ActiveAlarm._get_collection()
            coll.bulk_write(self.alarm_log)
        self.object.save()

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
            if (now - self.object.get_next(num)).total_seconds() < -1:
                # if (now - self.object.get_next(num)).total_seconds() < int(item.delay):
                break
            self.logger.info("...")
            if not item.member:
                self.logger.warning("Unknown escalation member: %s", item.member)
                continue
            escalation = self.object.get_escalation(member=item.member, key=item.get_key())
            if escalation and escalation.status == EscalationStatus.OK:
                # Already escalated
                if item.repeat and (not item.max_repeats or escalation.repeats < item.max_repeats):
                    escalation.repeats += 1
                else:
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
            # Execute Diagnostic
            if item.stop_processing:
                self.logger.debug("Stopping processing")
                self.remove_job()
        else:
            self.end_sequence()

    def check_escalation_waited(self, e_ctx, changed: bool = False):
        """
        Retry escalation waited and temp error
        Args:
            e_ctx: Escalation Context
            changed: Was Changed
        """
        from noc.main.models.template import Template

        for item in self.object.escalations:
            self.logger.info("Check waited: %s/%s", changed, item.status)
            if (
                item.status != EscalationStatus.TEMP
                and not (changed and item.status == EscalationStatus.OK)
            ) or item.deescalation_status:
                continue
            # Render TT subject and body
            template = Template.get_by_id(item.template)
            if not template:
                self.logger.info("No escalation template, skipping")
                self.log_alarm("No escalation template, skipping")
                return
            subject = template.render_subject(**e_ctx)
            body = template.render_body(**e_ctx)
            # retry action
            if item.member == EscalationMember.TT_SYSTEM:
                tt_system = TTSystem.get_by_id(item.key)
                if item.status == EscalationStatus.OK and changed:
                    # Changed
                    r = self.create_tt(tt_system, subject, body, e_ctx, tt_id=item.document_id)
                    if r.status != EscalationStatus.OK:
                        self.logger.info(
                            "[%s] Error when update message: %s", item.document_id, r.error
                        )
                        continue
                elif item.status == EscalationStatus.TEMP:
                    # Temporary error, repeat
                    r = self.create_tt(tt_system, subject, body, e_ctx)
                    if r.status == EscalationStatus.OK and r.document:
                        item.status = r.status
                        item.document_id = r.document
                else:
                    self.logger.info("Nothing waited")
                    return

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
                EscalationStatus.OK,
                EscalationStatus.FAIL,
            ):
                continue
            if item.member == EscalationMember.TT_SYSTEM and item.document_id:
                tt = TTSystem.get_by_id(item.key)
                r = self.close_tt(tt, item.document_id)
            elif item.member == EscalationMember.NOTIFICATION_GROUP:
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

    def get_escalation_items(self, tt_system: TTSystem) -> List[ECtxItem]:
        """
        Args:
            tt_system: TTSystem for checked item

        """
        r = []
        for item in self.object.items:
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
            r.append(ei)
        return r

    def get_action_context(self) -> List[TTActionContext]:
        """
        Return Available Action Context for escalation

        """
        r = []
        for action in self.object.profile.get_actions():
            if action == TTAction.ACK and self.object.alarm.ack_user:
                r.append(
                    TTActionContext(
                        action=TTAction.UN_ACK, label=f"Ack by {self.object.alarm.ack_user}"
                    )
                )
                continue
            elif action == TTAction.UN_ACK and not self.object.alarm.ack_ts:
                continue
            r.append(TTActionContext(action=action))
        return r

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
        )
        return ctx

    def check_escalated(self):
        """
        Process escalation doc and fill already escalated alarms.
        Note: Must be called under the lock
        """
        alarms = [item.alarm for item in self.object.items]
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
            if (not esc_tt or item.alarm in esc_status) and item.is_new:
                self.logger.info("Alarm %s is already escalated with TT %s", item.alarm, "")
                item.escalation_status = ItemStatus.EXISTS
                # item.current_escalation = esc_status[item.alarm]
                # item.current_tt_id = esc_tt[item.alarm]

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: str,
        body: str,
        context: Optional[Dict[str, Any]] = None,
        tt_id: Optional[str] = None,
    ) -> EscalationResult:
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
            return r
        elif r.status == EscalationStatus.FAIL or not r.is_ok or not r.document:
            self.log_alarm(f"Failed to create TT: {r.error}")
            metrics["escalation_tt_fail"] += 1
            # self.object.alarm.log_message(f"Failed to escalate: {r.error}")
            return r
        if tt_id:
            return r
        # Project result to escalation items
        ctx_map: Dict[int:ItemStatus] = {}
        for item in ctx.items:
            try:
                e_status = item.get_status()
            except AttributeError:
                self.log_alarm(f"Adapter malfunction. Status for {item.id} is not set.")
                continue
            if e_status == EscalationStatus.OK:
                self.log_alarm(f"{item.id} is appended successfully")
                e_status = ItemStatus.CHANGED
            else:
                self.log_alarm(f"Failed to append {item.id}: {item._message} ({e_status})")
                e_status = ItemStatus.FAIL
            ctx_map[item.id] = e_status
        for item in self.object.items:
            if item.managed_object.id not in ctx_map:
                continue
            item.status = ctx_map[item.managed_object.id]
        metrics["escalation_tt_create"] += 1
        return r

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
        with self.get_tt_system_context(tt_system, tt_id) as ctx:
            ctx.close()
        r = ctx.get_result()
        if r.is_ok:
            metrics["escalation_tt_close"] += 1
            return r
        if r.status == EscalationStatus.TEMP:
            metrics["escalation_tt_close_retry"] += 1
            tt_system.register_failure()
            error = f"Temporary error detected while closing tt {tt_id}: {r.error}"
        elif r.status == EscalationStatus.FAIL:
            metrics[f"escalation_tt_close_fail"] += 1
            error = f"Failed to close tt {tt_id}: {ctx.error_text}"
        else:
            error = r.error
        self.logger.info(error)
        return r

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
            metrics[f"escalation_tt_comment_fail"] += 1
            error = f"Failed to add comment to {tt_id}: {r.error}"
        elif r.status == EscalationStatus.FAIL:
            metrics[f"escalation_tt_comment_fail"] += 1
            error = f"Failed to close tt {tt_id}: {ctx.error_text}"
        else:
            error = r.error
        self.logger.info(error)
        return r

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

    def alarm_ack(self, tt_system: Optional[TTSystem]):
        """
        Acknowledge alarm by tt_system or settings

        """
