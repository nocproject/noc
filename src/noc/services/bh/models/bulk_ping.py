# ---------------------------------------------------------------------
# Ping models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel


class PingRequest(BaseModel):
    addresses: list[str]
    timeout: int | None
    n: int = 1
    tos: int | None


class PingItem(BaseModel):
    address: str
    rtt: list[float | None]


class PingResponse(BaseModel):
    items: list[PingItem]
