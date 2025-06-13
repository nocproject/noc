# ----------------------------------------------------------------------
# EscalationContext
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import List, Optional
from datetime import datetime

# Third-party modules
from bson import ObjectId
from pydantic import BaseModel, PrivateAttr, Field


class EscalationStatus(enum.Enum):
    """
    Attributes:
        OK: Escalation Success
        TEMP: Temporary error, repeat needed
        FAIL: Escalation Fail
        SKIP: Escalation Skipped
        WAIT: Escalation Wait
    """

    OK = "ok"
    TEMP = "temp"
    FAIL = "fail"
    SKIP = "skip"
    WAIT = "wait"
    NEW = "new"
    # Ack - for acked alarm


class TTAction(enum.Enum):
    """
    Attributes:
        CREATE_TT: Create Document on TT System
        CLOSE_TT: Close Document on TT System
        ACK: Acknowledge alarm
        UN_ACK: UnAcknowledge alarm
        CLEAR: Clear Alarm
        LOG: Add Alarm Log
        SUBSCRIBE: Subscribe alarm changes
        NOTIFY: Send Notification
    """

    CREATE_TT = "create_tt"
    CLOSE_TT = "close_tt"
    ACK = "ack"
    UN_ACK = "un_ack"
    CLEAR = "clear"  # Reopen
    LOG = "log"
    SUBSCRIBE = "subscribe"
    NOTIFY = "notify"


class TTActionContext(BaseModel):
    action: TTAction
    label: Optional[str] = None


class TTSystemConfig(BaseModel):
    """
    Attributes:
        login: TTSystem loging
        telemetry_sample: Telemetry Sample. 1 - all, 0 - Disable
        max_escalation_retries: Maximum number retries TempError escalation. 0 - disable
        global_limit: Number for create tt on 60 sec
        actions: Supported action list
        promote_item: Supported Escalation Item
        promote_group_tt: Escalate Group Item (Multiple Item)
    """

    login: str
    pre_reason: Optional[str] = None
    telemetry_sample: int = 0
    max_escalation_retries: int = 30
    global_limit: Optional[int] = None
    actions: Optional[List[TTAction]] = None
    promote_item: str = "D"
    promote_group_tt: bool = False


class EscalationResult(BaseModel):
    """
    Managed object item.

    Attributes:
        status: Escalation Status
        error: Error message description
        document: Escalation TT ID
    """

    status: EscalationStatus = EscalationStatus.OK
    error: Optional[str] = None
    document: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        return self.status == EscalationStatus.OK


class TTChange(BaseModel):
    """
    Attributes:
        document_id: Document ID on update
        action: Update Action
        user: user ID (username or id)
        timestamp: Action timestamp
        message: Message text
    """

    document_id: str
    action: TTAction  # ack, n_ack, log, close, subscribe
    user: str
    change_id: Optional[str] = None  # Update Sequence Number
    timestamp: Optional[datetime] = None
    message: Optional[str] = None


class EscalationMember(enum.Enum):
    TT_SYSTEM = "tt_system"
    NOTIFICATION_GROUP = "notification_group"
    # ack
    # n_ack
    # assign user
    # Diagnostic
    HANDLER = "handler"


class EscalationServiceItem(BaseModel):
    """
    Service Object Item
    Attributes:
        id: Service Id
        tt_id: ID on Escalation System
        oper_status ?
    """

    id: str
    tt_id: str


class EscalationItem(BaseModel):
    """
    Managed object item.

    Attributes:
        id: Managed Object's id in NOC database.
        tt_id: Managed Object's id in TT system.
    """

    id: int
    tt_id: str
    _status: Optional[EscalationStatus] = PrivateAttr()
    _message: Optional[str] = PrivateAttr()

    def set_ok(self) -> None:
        """Mark item as processed successfully."""
        self._status = EscalationStatus.OK

    def set_fail(self, msg: str) -> None:
        """Mark item as failed."""
        self._status = EscalationStatus.FAIL
        self._message = msg

    def set_temp(self, msg: str) -> None:
        """Mark item as temporary."""
        self._status = EscalationStatus.FAIL
        self._message = msg

    def get_status(self) -> EscalationStatus:
        """
        Get escalation status.

        Returns:
            Escalation status, if set. None otherwise.
        """
        return self._status


class EscalationContext(BaseModel):
    """
    Escalation context data class.

    This structure is passed to TTSystem
    during the escalation process.

    Attributes:
        subject: Rendered TT subject.
        body: Rendered TT body.
        queue: TT system's queue to place TT
        login: TT system's login
        timestamp: Alarm timestamp.
        is_unavailable: Alarm triggered unavailable items
        actions: Allowed Actions list
        items: Managed object references. Leader is first.
    """

    subject: str
    items: List[EscalationItem]
    services: Optional[List[EscalationServiceItem]] = None
    id: Optional[str] = None
    body: Optional[str] = None
    timestamp: Optional[datetime] = None
    queue: Optional[str] = None
    reason: Optional[str] = None
    login: Optional[str] = None
    actions: Optional[List[TTActionContext]] = None
    is_unavailable: bool = False

    @property
    def leader(self) -> EscalationItem:
        """
        Escalation leader.
        """
        return self.items[0]

    @property
    def service(self) -> Optional[EscalationServiceItem]:
        if self.services:
            return self.services[0]


class DeescalationContext(BaseModel):
    """
    Deescalation context data class.

    Args:
        id: TT id.
        subject: Rendered message subject.
        body: Rendered message body.
        queue: TT system's queue to search TT
        login: TT system's login
        timestamp: Alarm timestamp.
        is_unavailable: Alarm triggered unavailable items
    """

    id: str
    queue: Optional[str] = None
    login: Optional[str] = None
    timestamp: Optional[datetime] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    is_unavailable: bool = False


class TTRef(BaseModel):
    """
    External system reference.

    Args:
        id: External id
        description: Textual description.
    """

    id: str
    description: str


class TTCommentInfo(BaseModel):
    """
    Trouble Ticket comment.
    """

    body: str
    ts: Optional[datetime] = None
    login: Optional[str] = None
    subject: Optional[str] = None
    reply_to: Optional[str] = None


class TTInfo(BaseModel):
    """
    Trouble ticket information.
    """

    id: str
    queue: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    is_resolved: bool = False
    stage: TTRef
    timestamp: datetime
    close_timestamp: Optional[datetime] = None
    owner: Optional[TTRef] = None
    pre_reason: TTRef
    final_reason: Optional[TTRef] = None
    dept: Optional[TTRef] = None
    close_dept: Optional[TTRef] = None
    comments: Optional[List[TTCommentInfo]] = None


class TTCommentRequest(BaseModel):
    id: str
    body: str
    ts: Optional[datetime] = None
    login: Optional[str] = None
    subject: Optional[str] = None
    reply_to: Optional[str] = None


class EscalationGroupPolicy(enum.Enum):
    """
    Attributes:
        NEVER: Escalate only alarm
        ROOT: Escalate Root Cause group
        GROUP: Escalate group
        SERVICE: Escalate Service Affected Group
        CUSTOM: User former group
    """

    # Never Group, Alarm Only
    NEVER = 0
    # Escalate only first root cause in group
    ROOT = 1
    # Escalate any first alarm in the group
    GROUP = 2
    # Escalate
    SERVICE = 3
    #
    CUSTOM = 4  # handler ?
    # Escalate only first root cause in group
    # ROOT_FIRST = 1
    # Escalate only root causes
    # ROOT = 2
    # Escalate any first alarm in the group,
    # prefer root causes
    # ALWAYS_FIRST = 3
    # Always escalate
    # ALWAYS = 4


class ActionItem(BaseModel):
    """
    Item for actions
    Attributes:
        alarm: Alarm instance Id
        group: Alarm Group Reference
        service: Service Id (for service-alarm escalation)
    """
    alarm: str
    group: Optional[bytes] = None
    service: Optional[str] = None


class Action(BaseModel):
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
    action: TTAction
    key: Optional[str] = None
    delay: int = 0
    ack: str = "any"
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


class EscalationRequest(BaseModel):
    """
    Attributes:
        id: Escalation Id
        item: Escalation Item: Alarm | Group | Service
        policy: Item Policy
        actions: Action executed list
        start_at: start timestamp
        maintenance_policy: Action when item on maintenance
        end_condition: Condition when escalation end
        max_repeats: Repeat actions after last
        repeat_delay: Repeat interval
        ctx: Span Context id
        tt_system: Initial Action TT System Id
        user: Initial Action User
    """
    id: str = Field(default_factory=lambda: str(ObjectId()))
    # name: str
    #
    item: ActionItem
    policy: EscalationGroupPolicy = EscalationGroupPolicy.ROOT
    actions: List[Action]
    start_at: Optional[datetime] = None
    maintenance_policy: str = "e"
    end_condition: str = "CR"
    max_repeats: int = 0
    repeat_delay: int = 60
    # Span
    ctx: Optional[int] = None
    # From
    tt_system: Optional[str] = None
    user: Optional[int] = None
