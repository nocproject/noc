# ----------------------------------------------------------------------
# BuildingModel
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from datetime import date

# NOC modules
from .base import BaseModel
from .typing import Reference
from .admdiv import AdmDiv


class Building(BaseModel):
    id: str
    adm_division: Reference["AdmDiv"]
    postal_code: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    _csv_fields = ["id", "adm_division", "postal_code", "short_name", "start_date", "end_date"]
