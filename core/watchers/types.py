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
    WIPING = "wiping"
    SUSPEND_JOB = "suspend_job"
    DIAGNOSTIC_CHECK = "diagnostic_check"
    # Disaster ?
    # ?Lock change


@dataclass(frozen=True)
class WatchItem:
    """
    Item for watchers
    Attributes:
        effect: Watch effect
        key: Effect key
        after: Run watch after
        once: Remove after run
        wait_avail: Wait object available for run
        args: Additional arguments
    """

    effect: ObjectEffect
    # Match, Array
    key: Optional[str] = None
    after: Optional[datetime.datetime] = None
    once: bool = True
    wait_avail: bool = False
    remote_system: Optional[Any] = None
    # Reaction ? User ?, Reason
    args: Optional[Dict[str, str]] = None
