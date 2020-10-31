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
    description: Optional[str]
    type: str
    user: Optional[str]
    password: Optional[str]
    super_password: Optional[str]
    snmp_ro: Optional[str]
    snmp_rw: Optional[str]

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
