# ----------------------------------------------------------------------
# ResourceGroupModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel
from .typing import Reference


class ResourceGroup(BaseModel):
    id: str
    name: str
    technology: str
    parent: Reference["ResourceGroup"] | None = None
    description: str | None = None

    _csv_fields = ["id", "name", "technology", "parent", "description"]
