# ----------------------------------------------------------------------
# prefix datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from .utils import StateItem, ProjectItem


class PrefixProfileItem(BaseModel):
    id: str
    name: str


class VRFItem(BaseModel):
    id: str
    name: str


class ASItem(BaseModel):
    id: str
    name: str
    asf: str = Field(alias="as")


class PrefixDataStreamItem(BaseModel):
    id: str
    name: str
    change_id: str
    prefix: str
    afi: str
    source: str
    state: StateItem
    profile: PrefixProfileItem
    description: str | None
    labels: list[str] | None
    tags: list[str] | None
    project: ProjectItem | None
    vrf: VRFItem | None
    asf: ASItem | None = Field(None, alias="as")
