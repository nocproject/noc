# ----------------------------------------------------------------------
# Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import enum
from typing import Literal

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, Field

# NOC modules
from .enum import AlarmAction
from noc.core.models.escalationpolicy import EscalationPolicy
from noc.fm.models.alarmwatch import Effect


class WhenCondition(enum.Enum):
    ANY = "any"
    ON_END = "on_end"
    ON_START = "on_start"
    ON_CLEAR = "on_clear"


class ActionConfig(BaseModel):
    """
    Attributes:
        action: Run Action
        key: Action Key
        delay: Skip seconds after start
        ack: Alarm ack condition
        time_pattern: Time pattern, when allowed run
        min_severity: Min alarm severity for run
        max_retries: Max retries when Warning
        template: Template id for message
        stop_processing: Stop execute escalation if SUCCESS
        allow_fail: Allow run next actions if FAIL
    """

    action: AlarmAction
    key: str | None = None
    delay: int = 0
    ack: Literal["any", "ack", "unack"] = "any"
    when: WhenCondition = WhenCondition.ANY  # Manually, end sequence
    time_pattern: str | None = None
    min_severity: int | None = None
    has_effect: Effect | None = None
    ex_effect: Effect | None = None
    # Retry until - Disable, Count, TTL
    max_retries: int = 1
    template: str | None = None
    subject: str | None = None
    # TT System Settings
    pre_reason: str | None = None
    login: str | None = None  # queue
    queue: str | None = None
    promote_item_policy: str | None = None
    # End options
    stop_processing: bool = False
    allow_fail: bool = True
    register_message: bool = False
    # Approve Required
    # If approve required, it suspend processing and send
    # Message to approver
    manually: bool = False
    assigned: str | None = None
    # Manual, Group Access
    # root_only: bool = True
    # already_escalated


class ActionPermission(BaseModel):
    # By Role - Role, Role -> User, Group Map (Separate Config)
    user: int
    group: int
    tt_system: str


class AllowedAction(BaseModel):
    action: AlarmAction
    login: str | None = None
    access: list[ActionPermission] | None = None
    stop_processing: bool = False


class ActionItem(BaseModel):
    """
    Item for actions
    Attributes:
        alarm: Alarm instance Id
        group: Alarm Group Reference
        # service: Service Id (for service-alarm escalation)
    """

    alarm: str
    group: bytes | None = None
    # service: Optional[str] = None


class AlarmActionRequest(BaseModel):
    """
    Attributes:
        id: Escalation Id
        item: Escalation Item: Alarm | Group | Service
        actions: Action executed list
        start_at: start timestamp
        max_repeats: Repeat actions after last
        repeat_delay: Repeat interval
        ctx: Span Context id
        tt_system: Initial Action TT System Id
        user: Initial Action User
    """

    id: str = Field(default_factory=lambda: str(ObjectId()))
    actions: list[ActionConfig]
    allowed_actions: list[AllowedAction] | None = None
    start_at: datetime.datetime | None = None
    item: ActionItem | None = None
    item_policy: EscalationPolicy = EscalationPolicy.ROOT
    # Group
    end_condition: Literal["CR", "CA", "CT", "M", "E"] = "CR"
    # policy: EscalationPolicy = EscalationPolicy.ROOT
    # tt_system
    # Repeat action
    max_repeats: int = 0
    # Repeat Until
    repeat_delay: int = 60
    # Span
    ctx: int | None = None
    name: str | None = None
    # From
    tt_system: str | None = None
    user: int | None = None
