# ----------------------------------------------------------------------
# datastream models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Dict, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.cfgactions import ActionType


class RemoteSystemItem(BaseModel):
    id: str
    name: str


class WorkflowItem(BaseModel):
    id: str
    name: str


class StateItem(BaseModel):
    id: str
    name: str
    workflow: WorkflowItem
    allocated_till: Optional[datetime.datetime]


class ProjectItem(BaseModel):
    id: str
    name: str


class RemoteMapItem(BaseModel):
    remote_system: RemoteSystemItem
    remote_id: str


class DisposeAction(BaseModel):
    """
    # Action
    # Run command
    # Run diagnostic
    # Run discovery (all/config)
    # Send workflow event
    # Set Diagnostic -> UP/DOWN
    # Audit
    """

    action: ActionType
    key: str
    # checks
    args: Optional[Dict[str, Any]] = None


class DisposeTargetObject(BaseModel):
    model: str = "sa.ManagedObject"
    actions: Optional[List[DisposeAction]] = None
    is_agent: bool = False
    # CPE, Agent
    # audit


class DisposeResource(BaseModel):
    model: str
    actions: Optional[List[DisposeAction]]
