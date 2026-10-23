# ----------------------------------------------------------------------
# AuthProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class AuthProfile(BaseModel):
    id: str
    name: str
    description: str | None = None
    type: str = "S"
    user: str | None = None
    password: str | None = None
    super_password: str | None = None
    snmp_ro: str | None = None
    snmp_rw: str | None = None

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
