# ----------------------------------------------------------------------
# dnszone datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel


class DNSZoneRecord(BaseModel):
    name: str
    type: str
    rdata: str
    ttl: Optional[int]
    priority: Optional[int]


class DNSZoneDataStreamItem(BaseModel):
    id: str
    change_id: str
    name: str
    serial: str
    masters: List[str]
    slaves: List[str]
    records: List[DNSZoneRecord]
