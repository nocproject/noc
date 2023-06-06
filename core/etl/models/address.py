# ----------------------------------------------------------------------
# AddressModel
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel
from .typing import Reference
from .building import Building
from .street import Street


class Address(BaseModel):
    id: str
    building: Reference["Building"]
    street: Reference["Street"]
    num: int
    num_letter: Optional[str] = None

    _csv_fields = ["id", "building", "street", "num", "num_letter"]
