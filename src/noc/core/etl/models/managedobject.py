# ----------------------------------------------------------------------
# ManagedObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from enum import StrEnum

# Third-party modules
from pydantic import ConfigDict, IPvAnyAddress, field_validator

# NOC modules
from .base import BaseModel
from .typing import Reference, MappingItem, CapsItem, DomainName
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


class SourceType(StrEnum):
    d = "d"  # Disable
    m = "m"  # Management Address
    s = "s"  # Specify address
    # Loopback address
    l = "l"  # noqa
    a = "a"  # All interface addresses


class ManagedObject(BaseModel):
    id: str
    name: str
    # Workflow state
    state: str | None = None
    # Last state change
    state_changed: datetime.datetime | None = None
    # Workflow event
    event: str | None = None
    container: Reference["Object"] | None = None
    administrative_domain: Reference["AdministrativeDomain"]
    pool: str
    fm_pool: str | None = None
    segment: Reference["NetworkSegment"]
    profile: str | None = None
    object_profile: Reference["ManagedObjectProfile"]
    static_client_groups: list[Reference["ResourceGroup"]] | None = None
    static_service_groups: list[Reference["ResourceGroup"]] | None = None
    scheme: str
    address: str | None = None
    fqdn: DomainName | None = None
    port: str | None = None
    user: str | None = None
    password: str | None = None
    super_password: str | None = None
    snmp_ro: str | None = None
    trap_source_type: SourceType | None = SourceType.d
    trap_source_ip: str | None = None
    syslog_source_type: SourceType | None = SourceType.d
    syslog_source_ip: str | None = None
    description: str | None = None
    auth_profile: Reference["AuthProfile"] | None = None
    controller: Reference["ManagedObject"] | None = None
    l2_domain: Reference["L2Domain"] | None = None
    vrf: Reference["IPVRF"] | None = None
    labels: list[str] | None = None
    tt_system: Reference["TTSystem"] | None = None
    tt_queue: str | None = None
    tt_system_id: str | None = None
    project: Reference["Project"] | None = None
    capabilities: list[CapsItem] | None = None
    checkpoint: str | None = None
    mappings: list[MappingItem] | None = None

    @field_validator("address")
    @classmethod
    def address_must_ipaddress(cls, v: str) -> str | None:
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
