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


class ObjectData(_BaseModel):
    interface: str
    attr: str
    value: Any
    scope: Optional[str]


class Object(BaseModel):
    id: str
    name: str
    model: str
    data: List[ObjectData] = []
    container: Optional[Reference["Object"]]
    checkpoint: Optional[str]
