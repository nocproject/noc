# ----------------------------------------------------------------------
# AdmDivModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel
from .typing import Reference


class AdmDiv(BaseModel):
    id: str
    name: str
    parent: Optional[Reference["AdmDiv"]] = None
    short_name: Optional[str] = None

    _csv_fields = ["id", "parent", "name", "short_name"]
