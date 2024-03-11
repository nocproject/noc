# ----------------------------------------------------------------------
# Purgatorium utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import socket
import struct
from typing import Optional, Dict, List, Literal
from dataclasses import dataclass

# Third-party modules
import orjson

# NOC services
from noc.core.service.loader import get_service


@dataclass
class Message(object):
    value: bytes
    headers: Dict[str, bytes]
    timestamp: int
    key: int


PURGATORIUM_TABLE = "purgatorium"
ETL_SOURCE = "etl"
SCAN_SOURCE = "network-scan"
MANUAL_SOURCE = "manual"
SNMP_TRAP_SOURCE = "snmptrap"
NEIGHBOR_SOURCE = "neighbor"
SOURCES = {ETL_SOURCE, MANUAL_SOURCE, SCAN_SOURCE, SNMP_TRAP_SOURCE, NEIGHBOR_SOURCE}


@dataclass
class ProtocolCheckResult:
    check: Literal["ICMP", "HTTP", "SSH", "TELNET", "TCP", "SNMP"]
    status: bool  # Available && Access && Check
    port: Optional[int] = None
    available: Optional[bool] = None  # Protocol (port) is available, for UDP equal to access
    access: Optional[bool] = None  # None if not check (if available False)
    credential: Optional[str] = None  # Set if access True
    data: Dict[str, str] = None
    error: Optional[str] = None  # Error message


def register(
    address: str,  # 0.0.0.0
    pool: int,
    source: str,
    description: Optional[str] = None,
    border: Optional[int] = None,
    chassis_id: Optional[str] = None,
    hostname: Optional[str] = None,
    remote_system: Optional[int] = None,
    remote_id: Optional[str] = None,
    uptime: Optional[int] = None,
    labels: Optional[List[str]] = None,
    is_delete: bool = False,
    checks: Optional[List[ProtocolCheckResult]] = None,
    **kwargs,
):
    """
    Register host on Purgatorium DB
    :param address: Host IP address, 0.0.0.0 if not find
    :param pool: Pool on found IP
    :param source: Source that found OP: etl, network-scan, neighbors, syslog-source, trap-source, manual
    :param description: sysDescription
    :param border: Device, that find host on neighbors
    :param chassis_id: ChassisID host
    :param hostname: Host Hostname
    :param remote_system: RemoteSystem from received host
    :param remote_id: Host ID on RemoteSystem
    :param uptime: Host Uptime
    :param labels: Some tags
    :param is_delete: Flag that host deleted
    :param checks: List Checks, that running on discovery
    :param kwargs: Some data about Host (used when received from RemoteSystem)
    :return:
    """
    # address = IP.prefix(address)
    now = datetime.datetime.now()
    svc = get_service()
    data = {
        "date": now.date().isoformat(),
        "ts": now.replace(microsecond=0).isoformat(),
        "ip": struct.unpack("!I", socket.inet_aton(address))[0],
        "pool": int(pool),
        "source": source,
        "is_delete": is_delete,
        "description": description or None,
    }
    if source == ETL_SOURCE and not remote_system:
        raise ValueError("Source ETL required RemoteSystem set")
    elif source == ETL_SOURCE and not remote_id:
        raise ValueError("With RemoteSystem, RemoteId must be set")
    elif source == ETL_SOURCE:
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
    if uptime is not None:
        data["uptime"] = int(uptime)
    if labels:
        data["labels"] = list(labels)
    if checks:
        data["checks"] = [orjson.dumps(c).decode("utf-8") for c in checks]
    svc.publish(orjson.dumps(data), f"ch.{PURGATORIUM_TABLE}")
