# ----------------------------------------------------------------------
# EscalationContext
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Any
from datetime import datetime

# Third-party modules
from pydantic import BaseModel, PrivateAttr


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
    label: str | None = None


class Attachment(BaseModel):
    filename: str
    body: bytes
    mime_type: str = "text/plain"
    # application/vnd.ms-excel
    url: str | None = None

    @property
    def size(self):
        return len(self.body)


class TTUser(BaseModel):
    id: str
    username: str
    remote_id: str | None = None


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
    pre_reason: str | None = None
    telemetry_sample: int = 0
    max_escalation_retries: int = 30
    global_limit: int | None = None
    actions: list[TTAction] | None = None
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
    error: str | None = None
    document: str | None = None

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
    change_id: str | None = None  # Update Sequence Number
    timestamp: datetime | None = None
    message: str | None = None


class EscalationMember(enum.Enum):
    TT_SYSTEM = "tt_system"
    NOTIFICATION_GROUP = "notification_group"
    HANDLER = "handler"


class EscalationItem(BaseModel):
    """
    Managed object item.

    Attributes:
        id: Managed Object's id in NOC database.
        tt_id: Managed Object's id in TT system.
    """

    id: str
    tt_id: str
    ctx: dict[str, Any] | None = None
    label: str | None = None
    item_status: str = "new"  # changed/removed
    item: str = "other"  # service, managed_object, container
    _status: EscalationStatus | None = PrivateAttr()
    _message: str | None = PrivateAttr()

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
    items: list[EscalationItem]
    id: str | None = None
    body: str | None = None
    timestamp: datetime | None = None
    queue: str | None = None
    reason: str | None = None
    login: str | None = None
    actions: list[TTActionContext] | None = None
    is_unavailable: bool = False
    assigned: TTUser | None = None
    attachments: list[Attachment] | None = None

    @property
    def leader(self) -> EscalationItem:
        """
        Escalation leader.
        """
        return self.items[0]

    @property
    def service(self) -> EscalationItem | None:
        for i in self.items:
            if i.item == "service":
                return i

    @property
    def managed_object(self) -> EscalationItem | None:
        for i in self.items:
            if i.item == "managed_object":
                return i

    @property
    def container(self) -> EscalationItem | None:
        """"""
        for i in self.items:
            if i.item == "container":
                return i


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
    queue: str | None = None
    login: str | None = None
    timestamp: datetime | None = None
    subject: str | None = None
    body: str | None = None
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
    ts: datetime | None = None
    login: str | None = None
    subject: str | None = None
    reply_to: str | None = None


class TTInfo(BaseModel):
    """
    Trouble ticket information.
    """

    id: str
    queue: str | None = None
    subject: str | None = None
    body: str | None = None
    is_resolved: bool = False
    stage: TTRef
    timestamp: datetime
    close_timestamp: datetime | None = None
    owner: TTRef | None = None
    pre_reason: TTRef
    final_reason: TTRef | None = None
    dept: TTRef | None = None
    close_dept: TTRef | None = None
    comments: list[TTCommentInfo] | None = None


class TTCommentRequest(BaseModel):
    id: str
    body: str
    queue: str | None = None
    ts: datetime | None = None
    login: str | None = None
    subject: str | None = None
    reply_to: str | None = None
    user: TTUser | None = None
