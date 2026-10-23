# ----------------------------------------------------------------------
# vrf datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import StateItem, ProjectItem


class AFIItem(BaseModel):
    ipv4: bool
    ipv6: bool


class VRFProfileItem(BaseModel):
    id: str
    name: str


class VRFGroupDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    vpn_id: str
    afi: AFIItem
    source: str
    state: StateItem
    profile: VRFProfileItem
    description: str | None
    rd: str | None
    labels: list[str] | None
    tags: list[str] | None
    project: ProjectItem | None
