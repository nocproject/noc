# ----------------------------------------------------------------------
# MeRequest and MeResponse
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel


class MeRequest(BaseModel):
    ...


class GroupItem(BaseModel):
    id: str
    name: str


class MeResponse(BaseModel):
    id: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    groups: List[GroupItem]
    language: str
