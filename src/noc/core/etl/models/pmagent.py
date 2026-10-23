# ----------------------------------------------------------------------
# PMAgentModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import IPvAnyAddress, field_validator

# NOC modules
from .base import BaseModel
from .typing import Reference, MappingItem, CapsItem, DomainName
from .managedobject import ManagedObject


class PMAgent(BaseModel):
    id: str
    name: str
    fqdn: DomainName | None = None
    addresses: list[str] | None = None
    description: str | None = None
    managed_object: Reference["ManagedObject"] | None = None
    # Workflow state
    state: str | None = None
    labels: list[str] = []
    capabilities: list[CapsItem] | None = None
    checkpoint: str | None = None
    mappings: list[MappingItem] | None = None

    @field_validator("addresses")
    @classmethod
    def address_must_ipaddress(cls, v: list[str]) -> list[str]:
        r = []
        for x in v or []:
            IPvAnyAddress(x)
            r.append(x.strip())
        return r or None
