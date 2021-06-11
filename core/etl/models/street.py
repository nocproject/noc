# ----------------------------------------------------------------------
# StreetModel
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from datetime import date

# NOC modules
from .base import BaseModel
from .typing import Reference
from .division import Division


class Street(BaseModel):
    id: str
    parent: Reference["Division"]
    oktmo: str
    name: str
    short_name: str
    start_date: Optional[date]
    end_date: Optional[date]
