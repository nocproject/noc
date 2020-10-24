# ----------------------------------------------------------------------
# SubscriberProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class SubscriberProfileModel(BaseModel):
    id: str
    name: str
    description: Optional[str]
    workflow: Optional[str]

    _csv_fields = ["id", "name", "description", "workflow"]
