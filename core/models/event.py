# ---------------------------------------------------------------------
# Event Message Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import enum
import datetime
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel


class EventSeverity(enum.Enum):
    CLEARED: 0
    INDETERMINATE: 1
    CRITICAL: 5
    MAJOR: 4
    MINOR: 3
    WARNING: 2


class EventSource(enum.Enum):
    SYSLOG = "syslog"
    SNMP_TRAP = "SNMP Trap"
    SYSTEM = "system"
    INTERNAL = "internal"
    WINEVENT = "winevent"
    OTHER = "other"


class Target(BaseModel):
    address: str  # IP Address message initiator
    name: str  # Name message initiator
    id: Optional[str]  # For ManagedObject message Send
    pool: Optional[str] = None  # Pool message receiver
    is_agent: bool = False  # Agent message send
    remote_id: Optional[str] = None  # Id on remote System that message Send
    service: Optional[str] = None  # Service ID (for monitoring integration) ?


class MessageType(BaseModel):
    """
    Description Metadata classification message
    """

    source: EventSource = EventSource.OTHER  # Format for parsed event
    id: Optional[str] = None  # Event type, purpose for format.
    # trap_id for SNMP, event_id for external, code for internal
    severity: EventSeverity = EventSeverity.INDETERMINATE  # Event severity level
    facility: str = None  # Event facility (for syslog)
    profile: Optional[str] = None  # Link to SA Profile for classification
    event_class: Optional[str] = None  # For PreClassified message
    # AlarmClass ? PreClassify alarm
    # EventClass ? Pre Classify event


class Var(BaseModel):
    name: str  # Variable Name
    value: str  # Variable Value
    scope: Optional[str] = None  # Scope for variable
    snmp_raw: bool = False  # SNMP Raw value

    def to_json(self):
        if self.scope:
            return {
                "name": self.name,
                "value": self.value,
                "scope": self.scope,
                "snmp_raw": self.snmp_raw,
            }
        return {"name": self.name, "value": self.value, "snmp_raw": self.snmp_raw}


class Event(BaseModel):
    """
    Message Body Type
    """

    ts: int  # Event Registered ts
    target: Target  # Message Sender Target
    data: List[Var]  # Message Vars
    id: Optional[str] = None
    type: MessageType = MessageType()
    remote_system: Optional[str] = None  # Remote System send event
    remote_id: Optional[str] = None  # Remote Id event on Remote System
    labels: Optional[List[str]] = None  # Event labels
    message: Optional[str] = None  # Event message string

    @property
    def timestamp(self):
        return datetime.datetime.fromtimestamp(self.ts)
