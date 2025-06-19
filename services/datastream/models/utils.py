# ----------------------------------------------------------------------
# datastream models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional

# Third-party modules
from pydantic import BaseModel


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
