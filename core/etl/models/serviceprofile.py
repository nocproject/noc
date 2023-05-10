# ----------------------------------------------------------------------
# ServiceProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class ServiceProfile(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    workflow: Optional[str] = None
    card_title_template: Optional[str] = None

    _csv_fields = ["id", "name", "description", "card_title_template"]
