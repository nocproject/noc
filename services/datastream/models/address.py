# ----------------------------------------------------------------------
# address datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

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
    description: Optional[str]
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    fqdn: Optional[str]
    mac: Optional[str]
    subinterface: Optional[str]
    profile: AddressProfileItem
    project: Optional[ProjectItem]
    vrf: Optional[VRFItem]
