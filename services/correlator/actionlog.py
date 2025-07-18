# Python modules
# ----------------------------------------------------------------------
# ActionLog item
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# NOC modules
from noc.core.fm.request import ActionConfig
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.timepattern import TimePattern
from noc.aaa.models.user import User
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.activealarm import ActiveAlarm, WatchItem, Effect


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
    """
    Action Part of log with Run"""

    def __init__(
        self,
        action: AlarmAction,
        key,
        # Match
        time_pattern: Optional[TimePattern] = None,
        min_severity: Optional[int] = None,
        alarm_ack: str = "any",
        when: str = "any",
        # Time ?
        subject: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        status: ActionStatus = ActionStatus.NEW,
        error: Optional[str] = None,
        # Stop processed after action
        stop_processing: bool = False,
        allow_fail: bool = True,
        # Source Task
        user: Optional[User] = None,
        tt_system: Optional[TTSystem] = None,
        document_id: Optional[str] = None,
        template: Optional[Template] = None,
        **kwargs,
    ):
        self.action = action
        self.key = key
        # To ctx ?
        self.template: Optional[Template] = template
        self.subject = subject
        self.timestamp = timestamp  # run_at
        self.status = status
        self.error = error
        self.document_id = document_id
        self.min_severity = min_severity or 0
        self.time_pattern: Optional[TimePattern] = time_pattern
        self.alarm_ack: str = alarm_ack or "any"
        self.when: str = when or "any"
        self.stop_processing = stop_processing
        self.allow_fail = allow_fail
        self.repeat_num = 0
        #
        self.user = user
        self.tt_system = tt_system
        #
        self.ctx = kwargs

    def __str__(self):
        return f"{self.action} ({self.key}): {self.status} ({self.timestamp})"

    def set_status(self, result: ActionResult):
        """Update Action result"""
        self.status = result.status
        self.error = result.error
        if result.ctx:
            self.ctx |= result.ctx

    def is_match(self, severity: int, timestamp: datetime.datetime, ack_user: Any):
        """Check job condition"""
        if severity < self.min_severity:
            return False
        elif self.time_pattern and not self.time_pattern.match(timestamp):
            return False
        elif self.alarm_ack == "ack" and not ack_user:
            return False
        elif self.alarm_ack == "unack" and ack_user:
            return False
        return True

    def get_ctx(
        self,
        document_id: Optional[str] = None,
        alarm_ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build action Context
        Args:
            document_id: External document on tt_system
            alarm_ctx: Alarm context
        """
        r: Dict[str, Any] = {"timestamp": self.timestamp}
        if (
            self.action == AlarmAction.CREATE_TT or self.action == AlarmAction.CLOSE_TT
        ) and self.key == "stub":
            r["tt_system"] = self.tt_system
            r["tt_id"] = self.document_id or document_id
        elif self.action == AlarmAction.CREATE_TT or self.action == AlarmAction.CLOSE_TT:
            r["tt_system"] = TTSystem.get_by_id(self.key)
            r["tt_id"] = self.document_id or document_id
        elif self.action == AlarmAction.NOTIFY:
            r["notification_group"] = NotificationGroup.get_by_id(int(self.key))
        if self.template:
            r["subject"] = self.template.render_subject(**alarm_ctx)
            r["body"] = self.template.render_body(**alarm_ctx)
            r["template"] = self.template
        elif self.subject:
            r["subject"] = self.subject
            r["body"] = ""
        if self.user:
            r["user"] = self.user
        if self.tt_system:
            r["requester"] = self.tt_system
        if self.ctx:
            r |= self.ctx
        return r

    def get_repeat(self, delay: int) -> "ActionLog":
        """
        Return repeated Action
        Args:
            delay: Repeat delay
        """
        return ActionLog(
            action=self.action,
            key=self.key,
            status=ActionStatus.NEW,
            timestamp=self.timestamp + datetime.timedelta(seconds=delay),
            time_pattern=self.time_pattern,
            alarm_ack=self.alarm_ack,
            when=self.when,
            min_severity=self.min_severity,
            allow_fail=self.allow_fail,
            stop_processing=self.stop_processing,
            repeat_num=self.repeat_num + 1,
            **self.ctx,
        )

    @classmethod
    def from_request(
        cls,
        action: ActionConfig,
        started_at: datetime.datetime,
        one_time: bool = False,
        user: Optional[int] = None,
        tt_system: Optional[str] = None,
        stub_tt_system: Optional[TTSystem] = None,
    ) -> "ActionLog":
        """
        Create Action from Request

        Args:
            action: Action Config
            started_at: Timestamp when start
            one_time: Only one run, do not Repeat
            user: User Who requested Action
            tt_system: TT System who requested Action
            stub_tt_system: TT system for test cases
        """
        if user:
            user = User.get_by_id(int(user))
        if tt_system:
            tt_system = TTSystem.get_by_id(tt_system)
        elif stub_tt_system:
            tt_system = stub_tt_system
        return ActionLog(
            action=action.action,
            key=action.key,
            template=Template.get_by_id(int(action.template)) if action.template else None,
            subject=action.subject,
            status=ActionStatus.NEW if not action.manually else ActionStatus.PENDING,
            timestamp=started_at + datetime.timedelta(seconds=action.delay),
            #
            time_pattern=action.time_pattern,
            alarm_ack=action.ack,
            when=action.when,
            min_severity=action.min_severity or 0,
            #
            allow_fail=action.allow_fail,
            stop_processing=action.stop_processing,
            # Ctx
            queue=action.queue,
            pre_reason=action.pre_reason,
            login=action.login,
            promote_item_policy=action.promote_item_policy,
            #
            # Source
            user=user,
            tt_system=tt_system,
        )

    @classmethod
    def from_state(cls, data: Dict[str, Any]) -> "ActionLog":
        """Restore Action Context from State Document"""
        user, tt_system, template = None, None, None
        if data.get("user"):
            user = User.get_by_id(int(data["user"]))
        if data.get("tt_system"):
            tt_system = TTSystem.get_by_id(data["tt_system"])
        if data.get("template"):
            template = Template.get_by_id(int(data["template"]))
        return ActionLog(
            action=AlarmAction(data["action"]),
            key=data["key"],
            time_pattern=data.get("time_pattern"),
            min_severity=data["min_severity"],
            alarm_ack=data["alarm_ack"],
            when=data["when"],
            timestamp=data["timestamp"],
            status=ActionStatus(data["status"]),
            error=data.get("error"),
            stop_processing=data["stop_processing"],
            allow_fail=data["allow_fail"],
            user=user,
            tt_system=tt_system,
            document_id=data.get("document_id"),
            template=template,
            subject=data.get("subject"),
            **data["ctx"] if "ctx" in data else {},
        )

    def get_state(self) -> Dict[str, Any]:
        """Getting Dict for action current state"""
        r = {
            "action": self.action.value,
            "key": self.key,
            "time_pattern": self.time_pattern,
            "min_severity": self.min_severity,
            "alarm_ack": self.alarm_ack,
            "when": self.when,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "error": self.error,
            "stop_processing": self.stop_processing,
            "allow_fail": self.allow_fail,
            "user": None,
            "tt_system": None,
            "document_id": self.document_id,
            "template": None,
            "subject": self.subject or None,
            "ctx": self.ctx,
        }
        if self.user:
            r["user"] = self.user.id
        if self.tt_system:
            r["tt_system"] = self.tt_system.id
        if self.template:
            r["template"] = self.template.id
        return r

    @classmethod
    def from_watch(
        cls, watch: WatchItem, alarm: ActiveAlarm, is_clear: bool = False
    ) -> List["ActionLog"]:
        """Restore Action Log from Watch"""
        # Restore documentID, From WATCH, From LOG ?
        r = []
        now = datetime.datetime.now()
        if watch.effect == Effect.TT_SYSTEM:
            tt_s, tt_id = watch.key.split(":")
            tt_s = TTSystem.get_by_name(tt_s)
            args = watch.args.copy()
            # Create TT
            if not watch.clear_only:
                # For TT System update Action
                if args.get("clear_template"):
                    args["template"] = Template.get_by_id(int(watch.args["clear_template"]))
                r += [
                    ActionLog(
                        action=AlarmAction.CREATE_TT,
                        key=str(tt_s.id),
                        document_id=tt_id,
                        timestamp=alarm.last_update,
                        # Set valid status
                        status=ActionStatus.PENDING,
                        **args,
                    )
                ]
            if is_clear:
                # For TT System clear_action
                if args.get("template"):
                    args["template"] = Template.get_by_id(int(watch.args["template"]))
                r += [
                    ActionLog(
                        action=AlarmAction.CLOSE_TT,
                        key=str(tt_s.id),
                        document_id=tt_id,
                        timestamp=now,
                        status=ActionStatus.NEW,
                        when="on_end",
                        **args,
                    )
                ]
        return r

    @classmethod
    def from_alarm(cls, alarm: ActiveAlarm, is_clear: bool = False) -> List["ActionLog"]:
        """"""
        r = []
        for w in alarm.watchers:
            r += ActionLog.from_watch(w, alarm, is_clear)
        return r
