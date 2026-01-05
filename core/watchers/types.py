# ---------------------------------------------------------------------
# Watch Mechanics Types
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import enum
import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

# NOC Modules
from noc.core.models.cfgactions import ActionType


class ObjectEffect(enum.Enum):
    """
    Effect to Object
    Attributes:
        SUBSCRIPTION: notification group subscription
        MAINTENANCE: Planned maintenance on Object
        WF_EVENT: Permanent Workflow Event on Object (For Allocate)
        WIPING: Object in removing state
    """

    SUBSCRIPTION = "subscription"
    MAINTENANCE = "maintenance"
    WF_EVENT = "wf_event"
    MX_EVENT = "mx_event"
    WIPING = "wiping"
    SUSPEND_JOB = "suspend_job"
    DIAGNOSTIC_CHECK = "diagnostic_check"
    # Disaster ?
    # ?Lock change


@dataclass(slots=True)
class WatchItem:
    """
    Item for watchers
    Attributes:
        effect: Watch effect
        key: Effect key
        after: Run watch after
        once: Remove after effect
        wait_avail: Run after object available
        args: Additional arguments
    """

    effect: ObjectEffect
    # Match, Array
    key: Optional[str] = None
    after: Optional[datetime.datetime] = None
    once: bool = True
    wait_avail: bool = False
    remote_system: Optional[Any] = None
    # deadline
    # Reaction ? User ?, Reason
    args: Optional[Dict[str, str]] = None

    def get_action(self) -> Optional[ActionType]:
        """Return Object Action"""
        if self.effect == ObjectEffect.WF_EVENT:
            return ActionType.FIRE_WF_EVENT
        if self.effect == ObjectEffect.MX_EVENT:
            return ActionType.FIRE_OBJ_EVENT
        return None
