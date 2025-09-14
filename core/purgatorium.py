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
from collections import defaultdict
from typing import Optional, Dict, List, Literal, Iterable, Tuple
from dataclasses import dataclass

# Third-party modules
import orjson
from bson import ObjectId

# NOC services
from noc.core.service.loader import get_service
from noc.config import config


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


PURGATORIUM_SQL = """
SELECT
    IPv4NumToString(ip) as address,
    pool,
    groupArray(source) as sources,
    groupArray((source, remote_system,
        map('hostname', hostname, 'description', description, 'uptime', toString(uptime), 'remote_id', remote_id, 'ts', toString(max_ts)),
         data, labels, service_groups, clients_groups, is_delete)) as all_data,
    groupUniqArrayArray(checks) as all_checks,
    groupUniqArrayArray(labels) as all_labels,
    groupUniqArray(router_id) as router_ids,
    max(last_ts) as last_ts
FROM (
    SELECT ip, pool, remote_system, source,
     argMax(is_delete, ts) as is_delete,
     argMax(hostname, ts) as hostname, argMax(description, ts) as description,
     argMax(uptime, ts) as uptime, argMax(remote_id, ts) as remote_id, argMax(checks, ts) as checks,
     argMax(data, ts) as data, argMax(labels, ts) as labels,
     argMax(service_groups, ts) as service_groups, argMax(clients_groups, ts) as clients_groups,
     argMax(router_id, ts) as router_id, argMax(ts, ts) as max_ts, argMax(ts, ts) as last_ts
    FROM noc.purgatorium
    WHERE date >= %s
    GROUP BY ip, pool, remote_system, source
    )
GROUP BY ip, pool
ORDER BY ip
FORMAT JSONEachRow
"""


@dataclass(slots=True, frozen=True)
class PurgatoriumData(object):
    """
    Data return from Purgatorium Table
    """

    source: str
    ts: Optional[datetime.datetime] = None
    remote_system: Optional[str] = None
    labels: Optional[List[str]] = None
    service_groups: Optional[List[ObjectId]] = None
    client_groups: Optional[List[ObjectId]] = None
    data: Optional[Dict[str, str]] = None
    event: Optional[str] = None  # Workflow Event
    is_delete: bool = False  # Delete Flag

    def __str__(self):
        if self.remote_system and self.is_delete:
            return f"|DELETE]{self.source}@{self.remote_system}]: {self.data}"
        elif self.remote_system:
            return f"{self.source}@{self.remote_system}:{self.data['remote_id']}({self.ts}): {self.data}"
        return f"{self.source}({self.ts}): {self.data}"

    @property
    def key(self) -> str:
        if not self.remote_system:
            return self.source
        return f"{self.source}@{self.remote_system}"

    @property
    def remote_id(self) -> Optional[str]:
        """"""
        if not self.remote_system:
            return None
        return self.data["remote_id"]


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
    router_id: Optional[str] = None,
    hostname: Optional[str] = None,
    remote_system: Optional[int] = None,
    remote_id: Optional[str] = None,
    uptime: Optional[int] = None,
    labels: Optional[List[str]] = None,
    service_groups: Optional[List[int]] = None,
    clients_groups: Optional[List[int]] = None,
    template: Optional[str] = None,
    is_delete: bool = False,
    checks: Optional[List[ProtocolCheckResult]] = None,
    **kwargs,
):
    """
    Register host on Purgatorium DB
    Args:
        address: Host IP address, 0.0.0.0 if not find
        pool: Pool on found IP
        source: Source that found OP: etl, network-scan, neighbors, syslog-source, trap-source, manual
        description: sysDescription
        border: Device, that find host on neighbors
        chassis_id: ChassisID host
        router_id: RouterID host (IP address)
        hostname: Host Hostname
        remote_system: RemoteSystem from received host
        remote_id: Host ID on RemoteSystem
        uptime: Host Uptime
        labels: Some tags
        service_groups: List of Resource Group instance
        clients_groups: List of Resource Group instance
        template: Using template (default template)
        is_delete: Flag that host deleted
        checks: List Checks, that running on discovery
        kwargs: Some data about Host (used when received from RemoteSystem)

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
    if service_groups:
        data["service_groups"] = [int(rg) for rg in service_groups]
    if clients_groups:
        data["clients_groups"] = [int(rg) for rg in clients_groups]
    if router_id and router_id != address:
        data["router_id"] = struct.unpack("!I", socket.inet_aton(router_id))[0]
    svc.publish(orjson.dumps(data), f"ch.{PURGATORIUM_TABLE}")


def iter_discovered_object(
    from_ts: Optional[datetime.datetime] = None,
    ip_address: Optional[str] = None,
) -> Iterable[
    Tuple[int, str, List[str], List[PurgatoriumData], List[ProtocolCheckResult], datetime.datetime]
]:
    """Iter Discovered Data by query"""
    from noc.core.clickhouse.connect import connection
    from noc.main.models.remotesystem import RemoteSystem
    from noc.inv.models.resourcegroup import ResourceGroup

    ch = connection()
    if not from_ts:
        from_ts = datetime.datetime.now() - datetime.timedelta(
            seconds=config.network_scan.purgatorium_ttl
        )
    r = ch.execute(PURGATORIUM_SQL, return_raw=True, args=[from_ts.date().isoformat()])
    for num, row in enumerate(r.splitlines(), start=1):
        row = orjson.loads(row)
        data = defaultdict(dict)
        d_labels = defaultdict(list)
        groups = defaultdict(list)
        # hostnames, descriptions, uptimes, all_data,
        for source, rs, d1, d2, labels, s_groups, c_groups, is_delete in row["all_data"]:
            # if is_delete:
            #     logger.debug("[%s] Detect deleted flag", row["address"])
            if not int(d1["uptime"]):
                # Filter 0 uptime
                del d1["uptime"]
            if not rs:
                del d1["remote_id"]
            if rs:
                rs = RemoteSystem.get_by_bi_id(rs)
                if not rs:
                    continue
                rs = rs.name
            # Check timestamp
            data[(source, rs)].update(d1 | d2)
            data[(source, rs)]["is_delete"] = bool(is_delete)
            d_labels[(source, rs)] = labels
            for rg in s_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "s")].append(rg.id)
            for rg in c_groups or []:
                rg = ResourceGroup.get_by_bi_id(rg)
                if rg:
                    groups[(source, rs, "c")].append(rg.id)
        p_data = tuple(
            PurgatoriumData(
                source=source,
                ts=datetime.datetime.fromisoformat(d.pop("ts")),
                remote_system=rs,
                data=d,
                labels=d_labels.get((source, rs)) or [],
                service_groups=groups.get((source, rs, "s")) or [],
                client_groups=groups.get((source, rs, "c")) or [],
                is_delete=bool(d.pop("is_delete")),
                event=d.pop("event", None),
            )
            for (source, rs), d in data.items()
        )
        checks = tuple(ProtocolCheckResult(**orjson.loads(c)) for c in row["all_checks"])
        last_ts = datetime.datetime.fromisoformat(row["last_ts"]).replace(microsecond=0)
        if ip_address and ip_address != row["address"]:
            continue
        yield row["pool"], row["address"], list(set(row["sources"])), p_data, checks, last_ts
