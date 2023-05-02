# ---------------------------------------------------------------------
# SNMP models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List, Tuple

# Third-party modules
from gufo.snmp import ValueType
from pydantic import BaseModel


class SNMPAddress(BaseModel):
    address: str
    community: str


class SNMPRequest(BaseModel):
    addresses: List[SNMPAddress]
    oid_filter: str
    timeout: Optional[int]
    tos: Optional[int]
    max_repetitions: int = 1


class SNMPItem(BaseModel):
    address: str
    objects: List[Tuple[str, ValueType]]
    error_code: Optional[str]


class SNMPResponse(BaseModel):
    items: List[SNMPItem]
