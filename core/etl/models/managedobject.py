# ----------------------------------------------------------------------
# ManagedObjectModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class ManagedObjectModel(BaseModel):
    id: str
    name: str
    is_managed: str
    container: str
    administrative_domain: str
    pool: str
    fm_pool: Optional[str]
    segment: str
    profile: str
    object_profile: str
    static_client_groups: str
    static_service_groups: str
    scheme: str
    address: str
    port: str
    user: Optional[str]
    password: Optional[str]
    super_password: Optional[str]
    snmp_ro: Optional[str]
    description: Optional[str]
    auth_profile: Optional[str]
    tags: Optional[str]
    tt_system: Optional[str]
    tt_queue: Optional[str]
    tt_system_id: Optional[str]
    project: Optional[str]

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
        "tags",
        "tt_system",
        "tt_queue",
        "tt_system_id",
        "project",
    ]
