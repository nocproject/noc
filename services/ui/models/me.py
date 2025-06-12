# ----------------------------------------------------------------------
# MeRequest and MeResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel, Field


class MeRequest(BaseModel): ...


class GroupItem(BaseModel):
    id: str
    name: str


class MeResponse(BaseModel):
    id: str
    username: str
    language: str
    groups: List[GroupItem]
    avatar_label: str = Field(
        title="Avatar Label", description="Letters to be used when avatar is missed or empty"
    )
    avatar_label_fg: str = Field(
        title="Avatar Label Foreground",
        description="CSS background to be used along with avatar_label",
    )
    avatar_label_bg: str = Field(
        title="Avatar Label Background",
        description="CSS background to be used along with avatar_label",
    )
    avatar_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
