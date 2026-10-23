# ----------------------------------------------------------------------
# ServiceProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class ServiceProfile(BaseModel):
    id: str
    name: str
    description: str | None = None
    workflow: str | None = None
    card_title_template: str | None = None

    _csv_fields = ["id", "name", "description", "card_title_template"]
