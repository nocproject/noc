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
    parent: Optional[Reference["AdmDiv"]]
    name: str
    short_name: Optional[str]

    _csv_fields = ["id", "parent", "name", "short_name"]
