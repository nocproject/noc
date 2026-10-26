# ----------------------------------------------------------------------
# NetworkSegmentProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from .base import BaseModel


class NetworkSegmentProfile(BaseModel):
    id: str
    name: str

    _csv_fields = ["id", "name"]
