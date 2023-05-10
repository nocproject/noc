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
from .admdiv import AdmDiv


class Street(BaseModel):
    id: str
    parent: Reference["AdmDiv"]
    name: str
    short_name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    _csv_fields = ["id", "parent", "name", "short_name", "start_date", "end_date"]
