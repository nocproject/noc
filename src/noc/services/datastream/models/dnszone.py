# ----------------------------------------------------------------------
# dnszone datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class DNSZoneRecord(BaseModel):
    name: str
    type: str
    rdata: str
    ttl: int | None
    priority: int | None


class DNSZoneDataStreamItem(BaseModel):
    id: str
    change_id: str
    name: str
    serial: str
    masters: list[str]
    slaves: list[str]
    records: list[DNSZoneRecord]
