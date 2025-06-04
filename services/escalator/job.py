# ----------------------------------------------------------------------
# Automation with processed alarm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import enum
from dataclasses import dataclass
from typing import List, Set, Iterable, Optional, Tuple, Dict, Any

# Third-party modules
from bson import ObjectId


# NOC modules
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.tt.types import (
    EscalationItem as ECtxItem,
    EscalationServiceItem,
    EscalationStatus,
    EscalationResult,
    EscalationMember,
    TTActionContext,
    TTAction,
    EscalationRequest,
)
from noc.core.tt.base import TTSystemCtx
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm

class ActionStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
    """

    WAITING = "w"
    NEW = "n"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"
    SKIP = "s"
    WAIT_END = "we"


class JobStatus(enum.Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `r` - Running
        * `S` - Suspended
        * `s` - Success
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * 'e' - End Wait
        * `c` - Cancelled
    """

    PENDING = "p"

class ItemStatus(enum.Enum):
    """
    Attributes:
        NEW: New items
        CHANGED: Items was changed
        FAIL: Failed when add to escalation
        EXISTS: Escalate over another doc
        REMOVED: Removed from escalation
    """

    NEW = "new"  # new item
    CHANGED = "changed"  # item changed
    FAIL = "fail"  # escalation fail
    EXISTS = "exists"  # Exists on another escalation
    REMOVED = "removed"  # item removed


@dataclass
class Item(object):
    """Over Job Item"""
    managed_object_id: int
    alarm: ObjectId
    status: ItemStatus = ItemStatus.NEW


@dataclass(frozen=True)
class ActionResult(object):
    status: ActionStatus
    error: str
    document_id: Optional[str] = None
    ctx: Optional[Dict[str, str]] = None


class Action(object):
    action: str

    def __init__(
        self,
        key,
        **kwargs,
    ):
        ...


class AlarmAutomationJob(object):
    """
    Runtime Alarm Automation
    """

    def __init__(
        self,
        name: str,
        delay: int,
        status: JobStatus,
        items: List[Item],
        # alarms_ids
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        id: Optional[str] = None,
        allow_fail: bool = False,
        logger: Optional[Any] = None,
    ):
        ...

    def run_action(
        self, action: TTAction, key: str, **ctx: Dict[str, str],
    ) -> ActionResult:
        """Execute action"""
