# ----------------------------------------------------------------------
# AuthProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class AuthProfile(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: str = "S"
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None

    _csv_fields = [
        "id",
        "name",
        "description",
        "type",
        "user",
        "password",
        "super_password",
        "snmp_ro",
        "snmp_rw",
    ]
