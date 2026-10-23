# ----------------------------------------------------------------------
# SubscriberProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class SubscriberProfile(BaseModel):
    id: str
    name: str
    description: str | None = None
    workflow: str | None = None

    _csv_fields = ["id", "name", "description", "workflow"]
