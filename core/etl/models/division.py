# ----------------------------------------------------------------------
# DivisionModel
# ----------------------------------------------------------------------
# Copyright (C) 2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class Division(BaseModel):
    id: str
    name: str
    start_date: Optional[str] = None
