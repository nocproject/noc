# ----------------------------------------------------------------------
# AdministrativeDomainModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel
from .typing import Reference


class AdministrativeDomain(BaseModel):
    id: str
    name: str
    parent: Reference["AdministrativeDomain"] | None = None
    default_pool: str | None = None

    _csv_fields = ["id", "name", "parent", "default_pool"]
