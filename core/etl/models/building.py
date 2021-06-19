# ----------------------------------------------------------------------
# BuildingModel
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


class Building(BaseModel):
    id: str
    oktmo: str
    adm_division: Reference["AdmDiv"]
    postal_code: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]

    _csv_fields = ["id", "oktmo", "adm_division", "postal_code", "start_date", "end_date"]
