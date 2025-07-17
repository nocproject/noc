# ---------------------------------------------------------------------
# Alarm Action Base Class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional, Any, Dict, List
from logging import Logger

# NOC modules
from noc.core.perf import metrics
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    TTActionContext,
)
from noc.core.tt.base import TTSystemCtx, TTAction
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.fm.request import AllowedAction
from noc.sa.models.service import Service
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.activealarm import ActiveAlarm
from noc.aaa.models.user import User
from .actionlog import ActionResult


class AlarmActionRunner(object):
    """
    Base class for run actions from config.
    Args:
        items: Alarms
        alarm_log: Bulk Alarm Log
    """

    def __init__(
        self,
        items: List[Any],
        allowed_actions: List[AlarmAction] = None,
        logger: Optional[Logger] = None,
        services: Optional[List[Service]] = None,
    ):
        self.items = items
        self.alarm: "ActiveAlarm" = items[0].alarm
        self.services: List[Service] = (
            list(Service.objects.filter(id__in=services)) if services else None
        )
        self.allowed_actions: List[AllowedAction] = allowed_actions
        self.logger = logger or logging.getLogger("AlarmActionRunner")
        self.alarm_log = []

    def run_action(
        self,
        action: AlarmAction,
        **ctx: Dict[str, str],
    ) -> ActionResult:
        """
        Execute action
        Args:
            action: Execute action
            ctx: Action context
        """
        match action:
            case AlarmAction.CREATE_TT:
                r = self.create_tt(**ctx)
            case AlarmAction.CLOSE_TT:
                r = self.close_tt(**ctx)
            case AlarmAction.CLEAR:
                r = self.alarm_clear(**ctx)
            case AlarmAction.ACK:
                r = self.alarm_ack(**ctx)
            case AlarmAction.UN_ACK:
                r = self.alarm_unack(**ctx)
            case AlarmAction.NOTIFY:
                # alarm.log_message(change.message, source=str(user))
                r = self.notify(**ctx)
            case AlarmAction.SUBSCRIBE:
                r = self.alarm_subscribe(**ctx)
            case AlarmAction.LOG:
                self.log_alarm(message=ctx["subject"])
                r = ActionResult(status=ActionStatus.SUCCESS)
            case _:
                raise NotImplementedError("Action %s not implemented" % action)
        return r

    def check_escalated(self, tt_system: TTSystem) -> Optional[str]:
        """Check alarm have tt_id for tt_system"""
        log = self.alarm.get_escalation_log(tt_system)
        if not log:
            return
        # Compare with tt_system
        tt, tt_id = log.tt_id.split(":")
        return tt_id.strip()

    def get_escalation_items(
        self, tt_system: TTSystem, promote_items: Optional[str] = None
    ) -> List[ECtxItem]:
        """
        Build escalation items for Escalation Doc
        Args:
            tt_system: TTSystem for checked item
            promote_items:

        """
        r = []
        for item in self.items:
            # if item.is_already_escalated:
            #     continue
            if not item.managed_object:
                continue
            if not item.managed_object.can_escalate(True, tt_system):
                err = f"Cannot append object {item.managed_object.name} to group tt: Escalations are disabled"
                self.log_alarm(err)
                # item.escalation_status = "fail"
                continue
            if not tt_system.get_object_tt_id(item.managed_object):
                err = f"Cannot append object {item.managed_object.name} to group tt: Belongs to other TT system"
                self.log_alarm(err)
                # item.escalation_status = "fail"
                continue
            ei = ECtxItem(
                id=str(item.managed_object.id),
                tt_id=tt_system.get_object_tt_id(item.managed_object),
            )
            r.append(ei)
        return r

    def get_affected_services_items(self, tt_system: TTSystem) -> List[EscalationServiceItem]:
        """Return Affected Service item for escalation doc"""
        r = []
        if not self.services:
            return r
        for svc in self.services:
            r.append(EscalationServiceItem(id=str(svc.id), tt_id=tt_system.get_object_tt_id(svc)))
        return r

    def get_action_context(self) -> List[TTActionContext]:
        """Return Available Action Context for escalation"""
        r = []
        for aa in self.allowed_actions:
            if aa.action == AlarmAction.ACK and self.alarm.ack_user:
                r.append(
                    TTActionContext(action=TTAction.UN_ACK, label=f"Ack by {self.alarm.ack_user}")
                )
                continue
            elif aa.action == AlarmAction.UN_ACK and not self.alarm.ack_ts:
                continue
            elif aa.action == AlarmAction.ACK:
                r.append(TTActionContext(action=TTAction.ACK))
            elif aa.action == AlarmAction.CLEAR:
                r.append(TTActionContext(action=TTAction.CLOSE))
        return r

    def get_tt_system_context(
        self,
        tt_system: TTSystem,
        tt_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        queue: Optional[str] = None,
        pre_reason: Optional[str] = None,
    ) -> TTSystemCtx:
        """
        Build TTSystem Context
        Args:
            tt_system: TTSystem instance
            tt_id: Document ID
            timestamp: Time when run Escalation
            login:
            queue: TT Queue
            pre_reason: Alarm Pre-Diagnostic code

        """
        # cfg = self.get_tt_system_config(tt_system)
        cfg = tt_system.get_config()
        if self.alarm.managed_object and not queue:
            queue = self.alarm.managed_object.tt_queue
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=queue,
            reason=pre_reason,
            login=login or cfg.login,
            timestamp=timestamp,
            actions=self.get_action_context(),
            items=self.get_escalation_items(tt_system, cfg.promote_item),
            services=self.get_affected_services_items(tt_system),
        )
        return ctx

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

    def get_bulk(self) -> List[Any]:
        return self.alarm_log

    def comment_tt(
        self,
        tt_system: TTSystem,
        tt_id: str,
        message: str,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        queue: Optional[str] = None,
        pre_reason: Optional[str] = None,
        **kwargs,
    ) -> EscalationResult:
        """
        Append Comment to Trouble Ticket

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            timestamp:
            message: comment message

        Returns:
            Escalation Resul instance
        """
        self.logger.info("Appending comment to TT %s:%s", tt_system, tt_id)
        with self.get_tt_system_context(
            tt_system, tt_id, timestamp, login, queue, pre_reason
        ) as ctx:
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
        self,
        user: User,
        requester: Optional[TTSystem] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        if requester:
            message = message or f"Acknowledge by {user} (from TTSystem: {requester.name})"
        else:
            message = message or f"Acknowledge by {user}"
        self.alarm.acknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_unack(
        self,
        user: User,
        requester: Optional[TTSystem] = None,
        message: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        **kwargs,
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        if requester:
            message = message or f"UnAcknowledge by {user} (from TTSystem: {requester.name})"
        else:
            message = message or f"UnAcknowledge by {user}"
        self.alarm.unacknowledge(user, message)
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_clear(
        self,
        user: User,
        requester: Optional[TTSystem] = None,
        message: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        **kwargs,
    ):
        """
        Clear alarm by tt_system or settings

        """
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        self.alarm.register_clear(
            message or f"Clear by: {user}",
            user=user,
            timestamp=timestamp,
        )
        # Delayed, checked action - status return other service
        return ActionResult(status=ActionStatus.SUCCESS)

    def alarm_subscribe(
        self,
        user: User,
        requester: Optional[TTSystem] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        self.alarm.subscribe(user)
        return ActionResult(status=ActionStatus.SUCCESS)

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: str,
        body: str,
        tt_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        queue: Optional[str] = None,
        pre_reason: Optional[str] = None,
        requester: Optional[TTSystem] = None,
        user: Optional[User] = None,
        **kwargs,
    ) -> ActionResult:
        """
        Create Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body
            login:
            tt_id: If set, do changes
            timestamp: Action timestamp
            requester: TTSystem, request action
            queue: TT Queue
            pre_reason: Diagnostic Pre Reason
            user: User, request action

        Returns:
            EscalationResult:
        """
        self.logger.debug(
            "Escalation message:\nSubject: %s\n%s",
            subject,
            body,
        )
        # Build Items for context
        tt_id = tt_id or self.check_escalated(tt_system)
        if tt_id:
            self.logger.info("Changed TT in system %s:%s", tt_system.name, tt_id)
            self.log_alarm(f"Changed TT in system {tt_system.name}")
        else:
            self.logger.info(
                "Creating TT in system %s (L:%s,Q:%s,R:%s)",
                tt_system.name,
                login,
                queue,
                pre_reason,
            )
            self.log_alarm(f"Creating TT in system {tt_system.name}")
        with self.get_tt_system_context(
            tt_system, tt_id, timestamp, login, queue, pre_reason
        ) as ctx:
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
            self.alarm.escalate(tt_system.get_tt_id(r.document))
            #
            self.alarm.safe_save()
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
        subject: Optional[str] = None,
        body: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        queue: Optional[str] = None,
        pre_reason: Optional[str] = None,
        requester: Optional[TTSystem] = None,
        user: Optional[User] = None,
        **kwargs,
    ) -> ActionResult:
        """
        Close Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            subject: Message Subject
            body: Message Body
            tt_id: Number of document on TT System
            pre_reason: comment message for close reason
            timestamp: Action timestamp
            login:
            queue:
            requester: TTSystem, request action
            user: User, request action

        Returns:
            Escalation Resul instance
        """
        if not tt_id:
            return ActionResult(status=ActionStatus.SKIP)
        self.logger.info("Closing TT %s:%s", tt_system, tt_id)
        subject = subject or "Alarm cleared"
        body = body or "Alarm has been cleared"
        with self.get_tt_system_context(
            tt_system, tt_id, timestamp, login, queue, pre_reason
        ) as ctx:
            ctx.close(subject, body)
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
