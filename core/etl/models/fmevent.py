# ----------------------------------------------------------------------
# FMEvent Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# NOC modules
from .base import BaseModel, _BaseModel
from noc.core.fm.event import Target


class Var(_BaseModel):
    name: str  # Variable Name
    value: str  # Variable Value


class RemoteObject(BaseModel):
    id: str = None  # For ManagedObject or Agent message Send
    name: str  # Name message initiator
    address: Optional[str]  # IP Address message initiator
    pool: Optional[str] = None  # Pool message receiver
    is_agent: bool = False  # Agent message send
    remote_id: Optional[str] = None  # Id on remote System that message Send
    remote_system: Optional[str] = None  #

    def get_target(self) -> Target:
        return Target(
            address=self.address,
            name=self.name,
            pool=self.pool,
            is_agent=self.is_agent,
            remote_id=self.remote_id,
        )


class FMEventObject(BaseModel):
    id: str  # Event Id
    ts: int  # Event Registered ts
    object: RemoteObject  # Message Send object
    data: List[Var]  # Message Vars
    severity: str
    event_class: Optional[str] = None
    is_cleared: bool = False  # Set flag for cleared severity
    labels: Optional[List[str]] = None  # Event labels
    message: Optional[str] = None  # Event message string
