# ----------------------------------------------------------------------
# NetworkSegmentProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseModel


class NetworkSegmentProfileModel(BaseModel):
    id: str
    name: str

    _csv_fields = ["id", "name"]
