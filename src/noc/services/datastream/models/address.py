# ----------------------------------------------------------------------
# address datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import StateItem, ProjectItem


class AddressProfileItem(BaseModel):
    id: str
    name: str


class VRFItem(BaseModel):
    id: str
    name: str


class AddressDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    address: str
    source: str
    state: StateItem
    description: str | None
    labels: list[str] | None
    tags: list[str] | None
    fqdn: str | None
    mac: str | None
    subinterface: str | None
    profile: AddressProfileItem
    project: ProjectItem | None
    vrf: VRFItem | None
