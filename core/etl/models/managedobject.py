# ----------------------------------------------------------------------
# ManagedObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Union
from enum import Enum
from pydantic import IPvAnyAddress, validator

# NOC modules
from .base import BaseModel, _BaseModel
from .typing import Reference
from .administrativedomain import AdministrativeDomain
from .authprofile import AuthProfile
from .object import Object
from .managedobjectprofile import ManagedObjectProfile
from .networksegment import NetworkSegment
from .resourcegroup import ResourceGroup
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


class ManagedObject(BaseModel):
    id: str
    name: str
    is_managed: bool
    container: Optional[Reference["Object"]]
    administrative_domain: Reference["AdministrativeDomain"]
    pool: str
    fm_pool: Optional[str]
    segment: Reference["NetworkSegment"]
    profile: str
    object_profile: Reference["ManagedObjectProfile"]
    static_client_groups: List[Reference["ResourceGroup"]]
    static_service_groups: List[Reference["ResourceGroup"]]
    scheme: str
    address: str
    port: Optional[str]
    user: Optional[str]
    password: Optional[str]
    super_password: Optional[str]
    snmp_ro: Optional[str]
    trap_source_type: Optional[SourceType] = SourceType.d
    trap_source_ip: Optional[str]
    syslog_source_type: Optional[SourceType] = SourceType.d
    syslog_source_ip: Optional[str]
    description: Optional[str]
    auth_profile: Optional[Reference["AuthProfile"]]
    labels: Optional[List[str]]
    tt_system: Optional[Reference["TTSystem"]]
    tt_queue: Optional[str]
    tt_system_id: Optional[str]
    project: Optional[Reference["Project"]]
    capabilities: Optional[List[CapsItem]]
    checkpoint: Optional[str]

    @validator("address")
    def address_must_ipaddress(cls, v):  # pylint: disable=no-self-argument
        IPvAnyAddress().validate(v)
        return str(v)

    class Config:
        fields = {"labels": "tags"}
        allow_population_by_field_name = True

    _csv_fields = [
        "id",
        "name",
        "is_managed",
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
