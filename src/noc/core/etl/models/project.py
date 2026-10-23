# ----------------------------------------------------------------------
# ProjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class Project(BaseModel):
    id: str
    name: str
    code: str
    description: str | None = None

    _csv_fields = ["id", "name", "code", "description"]
