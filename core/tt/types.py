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

# NOC modules
from noc.core.models.escalationpolicy import EscalationPolicy


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
        CREATE: Create Document on TT System
        ACK: Acknowledge alarm
        UN_ACK: UnAcknowledge alarm
        CLOSE: Clear Alarm
        LOG: Add Alarm Log
        SUBSCRIBE: Subscribe alarm changes
        NOTIFY: Send Notification
    """

    CREATE = "create"
    ACK = "ack"
    UN_ACK = "un_ack"
    CLOSE = "clear"  # Reopen
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
    telemetry_sample: int = 0
    max_escalation_retries: int = 30
    global_limit: Optional[int] = None
    actions: Optional[List[TTAction]] = None
    promote_item: bool = False
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


class EscalationStep(BaseModel):
    delay: int
    member: EscalationMember
    key: str
    ack: str = "any"
    template: str
    time_pattern: Optional[str] = None
    min_severity: Optional[int] = None
    max_retries: int = 0
    close_template: Optional[str] = None
    stop_processing: bool = False
    # Timestamp?


class EscalationRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    name: str
    timestamp: datetime
    steps: List[EscalationStep]
    # ctx
    # actions
    items_policy: EscalationPolicy = EscalationPolicy.ROOT
    maintenance_policy: str = "e"
    end_condition: str = "a"
    repeat_policy: str = "N"
    repeat_delay: int = 60
