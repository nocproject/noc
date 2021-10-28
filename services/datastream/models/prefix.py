# ----------------------------------------------------------------------
# prefix datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

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
    description: Optional[str]
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    project: Optional[ProjectItem]
    vrf: Optional[VRFItem]
    asf: Optional[ASItem] = Field(None, alias="as")
