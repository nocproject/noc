# ----------------------------------------------------------------------
# PMAgentModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import IPvAnyAddress, field_validator

# NOC modules
from .base import BaseModel
from .typing import Reference, MappingItem, CapsItem, DomainName
from .managedobject import ManagedObject


class PMAgent(BaseModel):
    id: str
    name: str
    fqdn: Optional[DomainName] = None
    addresses: Optional[List[str]] = None
    description: Optional[str] = None
    managed_object: Optional[Reference["ManagedObject"]] = None
    # Workflow state
    state: Optional[str] = None
    labels: List[str] = []
    capabilities: Optional[List[CapsItem]] = None
    checkpoint: Optional[str] = None
    mappings: Optional[List[MappingItem]] = None

    @field_validator("addresses")
    @classmethod
    def address_must_ipaddress(cls, v: List[str]) -> List[str]:
        r = []
        for x in v or []:
            IPvAnyAddress(x)
            r.append(x.strip())
        return r or None
