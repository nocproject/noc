# ----------------------------------------------------------------------
# Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, Literal, List

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, Field

# NOC modules
from .enum import AlarmAction


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
    key: Optional[str] = None
    delay: int = 0
    ack: Literal["any", "ack", "unack"] = "any"
    when: Literal["any", "on_start", "on_end"] = "any"
    time_pattern: Optional[str] = None
    min_severity: Optional[int] = None
    max_retries: int = 1
    template: Optional[str] = None
    # pre_reason: Optional[str] = None
    login: Optional[str] = None
    stop_processing: bool = False
    allow_fail: bool = True
    manually: bool = False
    # Manual, Group Access
    # root_only: bool = True


class ActionItem(BaseModel):
    """
    Item for actions
    Attributes:
        alarm: Alarm instance Id
        group: Alarm Group Reference
        # service: Service Id (for service-alarm escalation)
    """

    alarm: str
    group: Optional[bytes] = None
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
    #
    actions: List[ActionConfig]
    start_at: Optional[datetime.datetime] = None
    item: Optional[ActionItem] = None
    # Repeat action
    max_repeats: int = 0
    repeat_delay: int = 60
    # Span
    ctx: Optional[int] = None
    # From
    tt_system: Optional[str] = None
    user: Optional[int] = None
