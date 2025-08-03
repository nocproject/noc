# ----------------------------------------------------------------------
# ManagedObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List, Union, Annotated
from enum import Enum
from pydantic import IPvAnyAddress, field_validator

# Third-party modules
from pydantic import ConfigDict, StringConstraints

# NOC modules
from .base import BaseModel, _BaseModel
from .typing import Reference, MappingItem
from .administrativedomain import AdministrativeDomain
from .authprofile import AuthProfile
from .object import Object
from .managedobjectprofile import ManagedObjectProfile
from .networksegment import NetworkSegment
from .resourcegroup import ResourceGroup
from .l2domain import L2Domain
from .ipvrf import IPVRF
from .ttsystem import TTSystem
from .project import Project


class SourceType(str, Enum):
    d = "d"  # Disable
    m = "m"  # Management Address
    s = "s"  # Specify address
    # Loopback address
    l = "l"  # noqa
    a = "a"  # All interface addresses


class CapsItem(_BaseModel):
    name: str
    value: Union[str, bool, int]


DomainName = Annotated[
    str,
    StringConstraints(
        pattern=r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
    ),
]


class ManagedObject(BaseModel):
    id: str
    name: str
    # Workflow state
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    container: Optional[Reference["Object"]] = None
    administrative_domain: Reference["AdministrativeDomain"]
    pool: str
    fm_pool: Optional[str] = None
    segment: Reference["NetworkSegment"]
    profile: Optional[str] = None
    object_profile: Reference["ManagedObjectProfile"]
    static_client_groups: Optional[List[Reference["ResourceGroup"]]] = None
    static_service_groups: Optional[List[Reference["ResourceGroup"]]] = None
    scheme: str
    address: Optional[str] = None
    fqdn: Optional[DomainName] = None
    port: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    snmp_ro: Optional[str] = None
    trap_source_type: Optional[SourceType] = SourceType.d
    trap_source_ip: Optional[str] = None
    syslog_source_type: Optional[SourceType] = SourceType.d
    syslog_source_ip: Optional[str] = None
    description: Optional[str] = None
    auth_profile: Optional[Reference["AuthProfile"]] = None
    controller: Optional[Reference["ManagedObject"]] = None
    l2_domain: Optional[Reference["L2Domain"]] = None
    vrf: Optional[Reference["IPVRF"]] = None
    labels: Optional[List[str]] = None
    tt_system: Optional[Reference["TTSystem"]] = None
    tt_queue: Optional[str] = None
    tt_system_id: Optional[str] = None
    project: Optional[Reference["Project"]] = None
    capabilities: Optional[List[CapsItem]] = None
    checkpoint: Optional[str] = None
    mappings: Optional[List[MappingItem]] = None

    @field_validator("address")
    @classmethod
    def address_must_ipaddress(cls, v: str) -> Optional[str]:
        if v:
            IPvAnyAddress(v)
            return v.strip()
        return None

    model_config = ConfigDict(exclude={"is_managed"}, populate_by_name=True)

    _csv_fields = [
        "id",
        "name",
        "container",
        "administrative_domain",
        "pool",
        "fm_pool",
        "segment",
        "profile",
        "object_profile",
        "static_client_groups",
        "static_service_groups",
        "scheme",
        "address",
        "port",
        "user",
        "password",
        "super_password",
        "snmp_ro",
        "description",
        "auth_profile",
        "labels",
        "tt_system",
        "tt_queue",
        "tt_system_id",
        "project",
    ]
