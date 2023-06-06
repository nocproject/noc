# ----------------------------------------------------------------------
# TTSystemModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class TTSystem(BaseModel):
    id: str
    name: str
    handler: Optional[str] = None
    connection: Optional[str] = None
    description: Optional[str] = None

    _csv_fields = ["id", "name", "handler", "connection", "description"]
