# ----------------------------------------------------------------------
# ObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# Third-party modules
from pydantic import Field

from .base import BaseModel, Reference, _BaseModel


class ObjectData(_BaseModel):
    interface: str
    attr: str
    value: Any
    scope: str | None = None


class Object(BaseModel):
    id: str
    name: str
    model: str
    data: list[ObjectData] = []
    parent: Reference["Object"] | None = Field(None, serialization_alias="container")
    checkpoint: str | None = None
