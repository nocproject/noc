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
from typing import Optional, Dict, Any

# NOC modules
from noc.core.fm.request import ActionConfig
from noc.core.fm.enum import AlarmAction, ActionStatus
from noc.core.timepattern import TimePattern
from noc.aaa.models.user import User
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.fm.models.ttsystem import TTSystem


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
        action: AlarmAction,
        key,
        # Match
        time_pattern: Optional[TimePattern] = None,
        min_severity: Optional[int] = None,
        alarm_ack: str = "any",
        when: str = "any",
        # Time ?
        timestamp: Optional[datetime.datetime] = None,
        status: ActionStatus = ActionStatus.NEW,
        error: Optional[str] = None,
        # Stop processed after action
        stop_processing: bool = False,
        allow_fail: bool = True,
        # Source Task
        user: Optional[int] = None,
        tt_system: Optional[str] = None,
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
        self.alarm_ack: str = alarm_ack or "any"
        self.when: str = when or "any"
        self.stop_processing = stop_processing
        self.allow_fail = allow_fail
        self.repeat_num = 0
        #
        self.user = User.get_by_id(user) if user else None
        self.tt_system = TTSystem.get_by_id(tt_system) if tt_system else None
        #
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

    def get_ctx(
        self,
        document_id: Optional[str] = None,
        action_ctx: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build action CTX"""
        r = {"timestamp": self.timestamp}
        if self.action == AlarmAction.CREATE_TT or self.action == AlarmAction.CLOSE_TT:
            r["tt_system"] = TTSystem.get_by_id(self.key)
            r["tt_id"] = self.document_id or document_id
        elif self.action == AlarmAction.NOTIFY:
            r["notification_group"] = NotificationGroup.get_by_id(int(self.key))
        if self.template:
            r["subject"] = self.template.render_subject(**action_ctx)
            r["body"] = self.template.render_body(**action_ctx)
        if self.user:
            r["user"] = self.user
        if self.tt_system:
            r["requester"] = self.tt_system
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
            time_pattern=self.time_pattern,
            alarm_ack=self.alarm_ack,
            when=self.when,
            min_severity=self.min_severity,
            allow_fail=self.allow_fail,
            stop_processing=self.stop_processing,
            repeat_num=self.repeat_num + 1,
        )

    @classmethod
    def from_request(
        cls,
        action: ActionConfig,
        started_at: datetime.datetime,
        one_time: bool = False,
        user: Optional[int] = None,
        tt_system: Optional[str] = None,
    ) -> "ActionLog":
        """Create Action from Request"""
        return ActionLog(
            action=action.action,
            key=action.key,
            template=action.template,
            status=ActionStatus.NEW if not action.manually else ActionStatus.PENDING,
            login=action.login,
            timestamp=started_at + datetime.timedelta(seconds=action.delay),
            #
            time_pattern=action.time_pattern,
            alarm_ack=action.ack,
            when=action.when,
            min_severity=action.min_severity or 0,
            #
            allow_fail=action.allow_fail,
            stop_processing=action.stop_processing,
            #
            # Source
            user=user,
            tt_system=tt_system,
        )

    @classmethod
    def from_state(cls, data: Dict[str, Any]) -> "ActionLog":
        """Create action from State Document"""
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
            user=data.get("user"),
            tt_system=data.get("tt_system"),
            document_id=data.get("document_id"),
            template=data.get("template"),
        )

    def get_state(self) -> Dict[str, Any]:
        """Getting Dict for action state"""
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
        }
        if self.user:
            r["user"] = self.user.id
        if self.tt_system:
            r["tt_system"] = self.tt_system.id
        if self.template:
            r["template"] = self.template.id
        return r
