# ---------------------------------------------------------------------
# SNMP models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

# Third-party modules
from gufo.snmp import ValueType
from pydantic import BaseModel


class SNMPAddress(BaseModel):
    address: str
    community: str


class SNMPRequest(BaseModel):
    addresses: list[SNMPAddress]
    oid_filter: str
    timeout: int | None
    tos: int | None
    max_repetitions: int = 1


class SNMPItem(BaseModel):
    address: str
    objects: list[tuple[str, ValueType]]
    error_code: str | None


class SNMPResponse(BaseModel):
    items: list[SNMPItem]
