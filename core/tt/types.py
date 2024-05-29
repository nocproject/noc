# ----------------------------------------------------------------------
# EscalationContext
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import List, Optional
from datetime import datetime

# Third-party modules
from pydantic import BaseModel, PrivateAttr


class EscalationStatus(enum.Enum):
    OK = "ok"  # escalation success
    TEMP = "temp"  # temporary error, repeat needed
    FAIL = "fail"  # escalation fail
    SKIP = "skip"  # Escalation Skipped
    WAIT = "wait"  # Escalation Wait
    # Ack - for acked alarm


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
        items: Managed object references. Leader is first.
    """

    subject: str
    items: List[EscalationItem]
    id: Optional[str] = None
    body: Optional[str] = None
    timestamp: Optional[datetime] = None
    queue: Optional[str] = None
    reason: Optional[str] = None
    login: Optional[str] = None
    is_unavailable: bool = False

    @property
    def leader(self) -> EscalationItem:
        """
        Escalation leader.
        """
        return self.items[0]


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

    ts: Optional[datetime]
    login: Optional[str]
    subject: Optional[str]
    body: str
    reply_to: Optional[str]


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
    ts: Optional[datetime]
    login: Optional[str]
    subject: Optional[str]
    body: str
    reply_to: Optional[str]


class TTConfig(BaseModel):
    """
    TT Config Flags: wait_tt, items, alarm_ack, run_action, clear_alarm, changes_severity, add_comment
    Capabilities Flag
    """
