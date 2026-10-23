# ----------------------------------------------------------------------
# datastream models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Any

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
    allocated_till: datetime.datetime | None


class ProjectItem(BaseModel):
    id: str
    name: str


class RemoteMapItem(BaseModel):
    remote_system: RemoteSystemItem
    remote_id: str


class AdministrativeDomain(BaseModel):
    id: str
    name: str
    remote_system: RemoteSystemItem | None = None
    remote_id: str | None = None


class Service(BaseModel):
    id: str
    bi_id: str


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
    args: dict[str, Any] | None = None
    model_id: str | None = None

    @property
    def is_target(self) -> bool:
        return not self.model_id or self.model_id == "sa.ManagedObject"


class ManagedObjectOpaque(BaseModel):
    id: str
    name: str
    adm_path: list[int]
    administrative_domain: AdministrativeDomain
    remote_system: RemoteSystemItem | None = None
    remote_id: str | None = None
    mappings: list[RemoteMapItem] | None = None
    services: list[Service] | None = None
