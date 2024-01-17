# ----------------------------------------------------------------------
# Purgatorium utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, Dict
import socket
import struct
from dataclasses import dataclass

# NOC services
from noc.core.service.loader import get_service
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
    border: Optional[int] = None,
    chassis_id: Optional[str] = None,
    hostname: Optional[str] = None,
    remote_system: Optional[int] = None,
    remote_id: Optional[str] = None,
    is_delete: bool = False,
    **kwargs,
):
    address = IP.prefix(address)
    now = datetime.datetime.now()
    svc = get_service()
    data = {
        "date": now.date().isoformat(),
        "ts": now.replace(microsecond=0).isoformat(),
        "address": struct.unpack("!I", socket.inet_aton(address))[0],
        "pool": int(pool),
        "source": source,
        "is_delete": is_delete,
        "description": description or None,
    }
    if source == "etl" and not remote_system:
        raise ValueError("Source ETL required RemoteSystem set")
    elif source == "etl" and not remote_id:
        raise ValueError("With RemoteSystem, RemoteId must be set")
    elif source == "etl":
        # Set for ETL
        data["remote_system"] = remote_system
        data["remote_id"] = remote_id
    elif source == "neighbors" and not border:
        raise ValueError("Source Neighbors required Border must be set")
    elif source == "neighbors":
        data["border"] = border
    if kwargs:
        data["data"] = {k: str(v) for k, v in kwargs.items()}
    if chassis_id:
        data["chassis_id"] = chassis_id
    if hostname:
        data["hostname"] = hostname
    svc.register_metrics(PURGATORIUM_TABLE, [data], key=bi_hash((pool, address)))
