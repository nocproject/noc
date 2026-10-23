# ----------------------------------------------------------------------
# TTSystemModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class TTSystem(BaseModel):
    id: str
    name: str
    handler: str | None = None
    connection: str | None = None
    description: str | None = None

    _csv_fields = ["id", "name", "handler", "connection", "description"]
