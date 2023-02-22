# ----------------------------------------------------------------------
# EscalationContext
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional
from datetime import datetime

# Third-party modules
from pydantic import BaseModel


class EscalationStatus(BaseModel):
    status: str
    msg: Optional[str] = None


class EscalationItem(BaseModel):
    """
    Managed object item.

    Attributes:
        id: Managed Object's id in NOC database.
        tt_id: Managed Object's id in TT system.
    """

    id: str
    tt_id: str
    _status: Optional[EscalationStatus] = None

    def set_ok(self) -> None:
        """Mark item as processed successfully."""
        self.__status = EscalationStatus(status="ok")

    def set_fail(self, msg: str) -> None:
        """Mark item as failed."""
        self.__status = EscalationStatus(status="fail", msg=msg)

    def set_temp(self, msg: str) -> None:
        """Mark item as temporary."""
        self.__status = EscalationStatus(status="temp", msg=msg)

    def get_status(self) -> EscalationStatus:
        """
        Get escalation status.

        Returns:
            Escalation status, if set. None otherwise.
        """
        return self.__status


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
        items: Managed object references. Leader is first.
    """

    queue: Optional[str]
    reason: Optional[str]
    login: Optional[str]
    timestamp: Optional[datetime]
    subject: str
    body: str
    items: List[EscalationItem]

    @property
    def leader(self) -> EscalationItem:
        """
        Escalation leader.
        """
        return self.items[0]


class TTRef(BaseModel):
    """
    External system reference.

    Args:
        id: External id
        description: Textual description.
    """

    id: str
    description: str


class TTComment(BaseModel):
    """
    Trouble Ticket comment.
    """

    id: str
    ts: Optional[datetime]
    login: Optional[TTRef]
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
    comments: Optional[List[TTComment]] = None
