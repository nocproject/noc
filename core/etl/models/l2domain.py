# ----------------------------------------------------------------------
# L2DomainModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel
from .typing import Reference


class L2Domain(BaseModel):
    id: str
    name: str

    _csv_fields = ["id", "name", "profile"]
