# ----------------------------------------------------------------------
# ResourceGroupModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel
from .typing import Reference


class ResourceGroup(BaseModel):
    id: str
    name: str
    technology: str
    parent: Optional[Reference["ResourceGroup"]] = None
    description: Optional[str] = None

    _csv_fields = ["id", "name", "technology", "parent", "description"]
