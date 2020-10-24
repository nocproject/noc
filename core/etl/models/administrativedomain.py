# ----------------------------------------------------------------------
# AdministrativeDomainModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class AdministrativeDomainModel(BaseModel):
    id: str
    name: str
    parent: Optional[str]
    default_pool: Optional[str]

    _csv_fields = ["id", "name", "parent", "default_pool"]
