# ----------------------------------------------------------------------
# purgatorium utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Any, Optional, Dict
import socket
import struct
from dataclasses import dataclass
from functools import partial

# NOC services
from noc.core.service.loader import get_service
from noc.core.comp import DEFAULT_ENCODING
from noc.core.ip import IP
from noc.core.bi.decorator import bi_hash


@dataclass
class Message(object):
    value: bytes
    headers: Dict[str, bytes]
    timestamp: int
    key: int


PURGATORIUM_TABLE = "purgatorium"


def register(
        address: str,
        pool: int,
        source: str,
        description: Optional[str] = None,
        chassis_id: Optional[str] = None,
        hostname: Optional[str] = None,
        remote_system: Optional[int] = None,
        remote_id: Optional[str] = None,
        **kwargs,
):

    now = datetime.datetime.now()
    svc = get_service()
    address = IP.prefix(address)
    if remote_system and not remote_id:
        raise ValueError("With RemoteSystem, RemoteId must be set")
    if remote_system:
        remote_system = int(remote_system)
    svc.register_metrics(
        PURGATORIUM_TABLE,
        [
            {
                "date": now.date().isoformat(),
                "ts": now.replace(microsecond=0).isoformat(),
                "address": struct.unpack("!I", socket.inet_aton(address))[0],
                "pool": int(pool),
                "source": source,
                "description": description or None,
                # chassis_id
                # hostname
                # data
                # # Set for reco
                # remote_system
                # remote_id
            }
        ],
        key=bi_hash((pool, address)),
    )

