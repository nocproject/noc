# ----------------------------------------------------------------------
# Alarm Action
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Literal

# Third-party modules
from pydantic import BaseModel

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
