# ----------------------------------------------------------------------
# AddressModel
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

from .base import BaseModel
from .building import Building
from .street import Street
from .typing import Reference


class Address(BaseModel):
    id: str
    building: Reference["Building"]
    street: Reference["Street"]
    num: int
    num_letter: str | None = None

    _csv_fields = ["id", "building", "street", "num", "num_letter"]
