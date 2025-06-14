# ---------------------------------------------------------------------
# Alarm Action Base Class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import operator
from typing import Optional, Any, Dict, List, Tuple
from logging import Logger

# NOC modules
from noc.core.perf import metrics
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    TTActionContext,
    TTAction,
)
from noc.core.tt.base import TTSystemCtx
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.serviceprofile import ServiceProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.service import Service
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.activealarm import ActiveAlarm
from noc.aaa.models.user import User
from noc.main.models.template import Template
from noc.services.escalator.actionlog import ActionResult
from .typing import ActionStatus


class GroupAction(object):
    """
    Base class for actions.

    Subclasses must override `execute` method.

    Args:
        items: Environment instance.
    """

    def __init__(
        self,
        items: List[Any],
        logger: Logger,
        services: Optional[List[Service]] = None,
        total_objects=None,
        total_subscribers=None,
        total_services=None,
    ):
        self.items = items
        self.alarm = items[0].alarm
        self.services: List[Service] = (
            list(Service.objects.filter(id__in=services)) if services else None
        )
        self.logger = logger
        self.alarm_log = []
        self.total_objects = total_objects or []
        self.total_subscribers = total_subscribers or []
        self.total_services = total_services or []

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

    def render_template(self, template) -> Tuple[str, str]:
        """"""
        ctx = self.get_ctx()
        return template.render_subject(**ctx), template.render_body(**ctx)

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
            "services": self.services,
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

    def get_escalation_items(self, tt_system: TTSystem) -> List[ECtxItem]:
        """
        Build escalation items for Escalation Doc
        Args:
            tt_system: TTSystem for checked item

        """
        r = []
        for item in self.items:
            # if item.is_already_escalated:
            #     continue
            # rid = item.managed_object.get_mapping(rs)
            # if rid:
            #     r.append(
            #         ECtxItem(id=str(item.managed_object.id), tt_id=rid),
            #     )
            #     continue
            if not item.managed_object.can_escalate(True):
                err = f"Cannot append object {item.managed_object.name} to group tt: Escalations are disabled"
                self.log_alarm(err)
                # item.escalation_status = "fail"
                continue
            if item.managed_object.tt_system != tt_system:
                err = f"Cannot append object {item.managed_object.name} to group tt: Belongs to other TT system"
                self.log_alarm(err)
                # item.escalation_status = "fail"
                continue
            ei = ECtxItem(id=str(item.managed_object.id), tt_id=item.managed_object.tt_system_id)
            r.append(ei)
        return r

    def get_affected_services_items(self) -> List[EscalationServiceItem]:
        """Return Affected Service item for escalation doc"""
        r = []
        for svc in self.services:
            r.append(
                EscalationServiceItem(
                    id=str(svc.id),
                    tt_id=svc.remote_id or "",
                )
            )
        return r

    def get_action_context(self, actions) -> List[TTActionContext]:
        """Return Available Action Context for escalation"""
        r = []
        for action in actions:
            if action == TTAction.ACK and self.alarm.ack_user:
                r.append(
                    TTActionContext(action=TTAction.UN_ACK, label=f"Ack by {self.alarm.ack_user}")
                )
                continue
            elif action == TTAction.UN_ACK and not self.alarm.ack_ts:
                continue
            r.append(TTActionContext(action=action))
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
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=self.alarm.managed_object.tt_queue,
            reason=None,
            login=login or cfg.login,
            timestamp=timestamp,
            actions=self.get_action_context(tt_system.get_actions()),
            items=self.get_escalation_items(tt_system) if cfg.promote_item else [],
            services=self.get_affected_services_items() or None,
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
            timestamp:
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
        self,
        user: User,
        requester: Optional[TTSystem] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        """
        Acknowledge alarm by tt_system or settings

        """
        message = message or f"Acknowledge by TTSystem: {requester.name}"
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
        message = message or f"UnAcknowledge by TTSystem: {requester.name}"
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
            f"Clear by TTSystem: {requester.name}",
            user=user,
            timestamp=timestamp,
        )
        # Delayed, checked action - status return other service
        return ActionResult(status=ActionStatus.SUCCESS)

    def create_tt(
        self,
        tt_system: TTSystem,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        template: Optional[Template] = None,
        tt_id: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
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
            template: Subject/Body template
            context: Escalation Context
            tt_id: If set, do changes
            timestamp: Action timestamp
            requester: TTSystem, request action
            user: User, request action

        Returns:
            EscalationResult:
        """
        if template:
            subject, body = self.render_template(template)
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
        template: Optional[Template] = None,
        reason: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        login: Optional[str] = None,
        requester: Optional[TTSystem] = None,
        user: Optional[User] = None,
        **kwargs,
    ) -> ActionResult:
        """
        Close Trouble Ticket on TT System

        Args:
            tt_system: TT System instance
            tt_id: Number of document on TT System
            reason: comment message for close reason
            timestamp: Action timestamp
            requester: TTSystem, request action
            user: User, request action

        Returns:
            Escalation Resul instance
        """
        if not tt_id:
            return ActionResult(status=ActionStatus.SKIP)
        self.logger.info("Closing TT %s:%s", tt_system, tt_id)
        subject, body = None, None
        if template:
            subject, body = self.render_template(template)
        with self.get_tt_system_context(tt_system, tt_id, timestamp, login) as ctx:
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
