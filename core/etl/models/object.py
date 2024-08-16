# ----------------------------------------------------------------------
# ObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Any

# NOC modules
from .base import BaseModel, Reference, _BaseModel
from pydantic import AliasPath, Field


class ObjectData(_BaseModel):
    interface: str
    attr: str
    value: Any
    scope: Optional[str] = None


class Object(BaseModel):
    id: str
    name: str
    model: str
    data: List[ObjectData] = []
    parent: Optional[Reference["Object"]] = Field(None, serialization_alias="container")
    checkpoint: Optional[str] = None
