# ----------------------------------------------------------------------
# AdmDivModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel
from .typing import Reference


class AdmDiv(BaseModel):
    id: str
    name: str
    parent: Reference["AdmDiv"] | None = None
    short_name: str | None = None

    _csv_fields = ["id", "parent", "name", "short_name"]
