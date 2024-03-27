# ----------------------------------------------------------------------
# cfgtrap datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, List
from collections import namedtuple

# NOC modules
from noc.core.datastream.base import DataStream
from noc.core.wf.diagnostic import SNMPTRAP_DIAG
from noc.core.ip import IP
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.main.models.timepattern import TimePattern
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject


class Target(
    namedtuple(
        "Target",
        [
            "mo_id",
            "name",
            "bi_id",
            "state",
            "pool",
            "fm_pool",
            "adm_domain",
            "adm_domain_name",
            "adm_domain_remote_system",
            "adm_domain_remote_id",
            "remote_system",
            "remote_id",
            "address",
            "labels",
            "effective_labels",
            "trap_community",
            "trap_source_ip",
            "trap_source_type",
            "event_processing_policy",
            "mop_event_processing_policy",
            "mop_trapcollector_storm_policy",
            "mop_trapcollector_storm_threshold",
            "syslog_source_ip",
            "syslog_source_type",
            "syslog_archive_policy",
            "mop_syslog_archive_policy",
            "time_pattern",
            "enable_ping",
            "ping_interval",
            "ping_policy",
            "ping_size",
            "ping_count",
            "ping_timeout_ms",
            "ping_time_expr_policy",
            "report_ping_rtt",
            "report_ping_attempts",
        ],
    )
):
    __slots__ = ()


class CfgTrapDataStream(DataStream):
    name = "cfgtarget"
    # DIAGNOSTIC = SNMPTRAP_DIAG  # !!
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id",
            "name",
            "bi_id",
            "state",
            "pool",
            "fm_pool",
            "administrative_domain",
            "administrative_domain__name",
            "administrative_domain__remote_system",
            "administrative_domain__remote_id",
            "remote_system",
            "remote_id",
            "address",
            "labels",
            "effective_labels",
            "trap_community",
            "trap_source_ip",
            "trap_source_type",
            "event_processing_policy",
            "object_profile__event_processing_policy",
            "object_profile__trapcollector_storm_policy",
            "object_profile__trapcollector_storm_threshold",
            "syslog_source_ip",
            "syslog_source_type",
            "syslog_archive_policy",
            "object_profile__syslog_archive_policy",
            "time_pattern",
            "object_profile__enable_ping",
            "object_profile__ping_interval",
            "object_profile__ping_policy",
            "object_profile__ping_size",
            "object_profile__ping_count",
            "object_profile__ping_timeout_ms",
            "object_profile__ping_time_expr_policy",
            "object_profile__report_ping_rtt",
            "object_profile__report_ping_attempts",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            name,
            bi_id,
            state,
            pool,
            fm_pool,
            adm_domain,
            adm_domain_name,
            adm_domain_remote_system,
            adm_domain_remote_id,
            remote_system,
            remote_id,
            address,
            labels,
            effective_labels,
            trap_community,
            trap_source_ip,
            trap_source_type,
            event_processing_policy,
            mop_event_processing_policy,
            mop_trapcollector_storm_policy,
            mop_trapcollector_storm_threshold,
            syslog_source_ip,
            syslog_source_type,
            syslog_archive_policy,
            mop_syslog_archive_policy,
            time_pattern,
            enable_ping,
            ping_interval,
            ping_policy,
            ping_size,
            ping_count,
            ping_timeout_ms,
            ping_time_expr_policy,
            report_ping_rtt,
            report_ping_attempts,
        ) = mo[0]
        target = Target(*mo[0])
        # Process event policy
        state = State.get_by_id(state)
        # Check if object capable to receive syslog events
        if not state.is_enabled_interaction("EVENT"):
            raise KeyError("Disabled by processed event by State")
        # Get effective event processing policy
        effective_epp = state.is_enabled_interaction("EVENT")
        effective_epp &= str(event_processing_policy) == "E" or (
            str(event_processing_policy) == "P" and str(mop_event_processing_policy) == "E"
        )
        # Get effective event archiving policy
        effective_sap = str(syslog_archive_policy) == "E" or (
            str(syslog_archive_policy) == "P" and str(mop_syslog_archive_policy) == "E"
        )
        #
        if trap_source_ip:
            ip = IP.prefix(trap_source_ip)
            if ip.is_internal:
                trap_source_ip = None
        if syslog_source_ip:
            ip = IP.prefix(syslog_source_ip)
            if ip.is_internal:
                syslog_source_ip = None
        # Process sources
        pool = str(Pool.get_by_id(pool).name)
        r = {
            "id": str(mo_id),
            "pool": pool,
            "fm_pool": str(Pool.get_by_id(fm_pool).name) if fm_pool else pool,
            "name": name,
            "bi_id": bi_id,
            "effective_labels": effective_labels,
            "addresses": [],
            "opaque_data": {
                "id": str(mo_id),
                "bi_id": str(bi_id),
                "name": name,
                "administrative_domain": {"id": adm_domain, "name": adm_domain_name},
                "labels": [
                    cls.qs(ll)
                    for ll in Label.objects.filter(
                        name__in=labels, expose_datastream=True
                    ).values_list("name")
                ],
            },
            "syslog": None,
            "trap": None,
            "ping": None,
        }
        # Ping Settings
        if enable_ping and ping_interval and ping_interval > 0:
            r["ping"] = {
                "interval": ping_interval,
                "policy": ping_policy,
                "size": ping_size,
                "count": ping_count,
                "timeout": ping_timeout_ms,
                "expr_policy": ping_time_expr_policy,
                "report_rtt": report_ping_rtt,
                "report_attempts": report_ping_attempts,
            }
        if time_pattern:
            r["time_expr"] = TimePattern.get_code(time_pattern)
        # Trap Settings
        if effective_epp and str(trap_source_type) != "d":
            r["trap"] = {
                "community": trap_community,
                "storm_policy": mop_trapcollector_storm_policy,
                "storm_threshold": mop_trapcollector_storm_threshold,
            }
        # Syslog Settings
        if effective_epp and str(trap_source_type) != "d":
            r["syslog"] = {
                "archive_events": effective_sap,
            }
        if not (bool(r["ping"]) or bool(r["syslog"]) or bool(r["trap"])):
            raise KeyError("Nothing Trap Source")
        # ManagedObject Opaque Data
        if remote_system:
            rs = RemoteSystem.get_by_id(remote_system)
            r["opaque_data"]["remote_system"] = {"id": str(rs.id), "name": rs.name}
            r["opaque_data"]["remote_id"] = remote_id
        if adm_domain_remote_system:
            rs = RemoteSystem.get_by_id(adm_domain_remote_system)
            r["opaque_data"]["administrative_domain"]["remote_system"] = {
                "id": str(rs.id),
                "name": rs.name,
            }
            r["opaque_data"]["administrative_domain"]["remote_id"] = adm_domain_remote_id
        addresses = {}
        # Process sources
        if address:
            addresses[address] = {
                    "address": address,
                    "is_fatal": True,
                    "interface": None,
                    "syslog_source": bool(r["syslog"]),
                    "trap_source": bool(r["trap"]),
                    "ping_check": bool(r["ping"]),
                }
        if str(trap_source_type) == "s" and trap_source_ip and trap_source_ip in addresses:
            r[trap_source_ip]["trap_source"] = True
        elif str(trap_source_type) == "s" and trap_source_ip:
            r[trap_source_ip] = {
                    "address": str(trap_source_ip),
                    "is_fatal": False,
                    "interface": None,
                    "syslog_source": False,
                    "trap_source": True,
                    "ping_check": False,
                }
        if str(syslog_source_type) == "s" and syslog_source_ip and syslog_source_ip in addresses:
            r[syslog_source_type]["syslog_source"] = True
        elif str(trap_source_type) == "s" and syslog_source_ip:
            r[trap_source_ip] = {
                    "address": str(syslog_source_ip),
                    "is_fatal": False,
                    "interface": None,
                    "syslog_source": False,
                    "trap_source": True,
                    "ping_check": False,
                }
        # Loopback address
        for a in cls._get_loopback_addresses(
            mo_id,
            trap=bool(r["trap"]) and trap_source_type == "l",
            syslog=bool(r["syslog"]) and syslog_source_type == "l",
            ping=bool(r["ping"]),
        ):
            if a["address"] in addresses:
                continue
            addresses[a["address"]] = a
        # if not r["addresses"]:
        #    raise KeyError("No Loopback interface with address")
        # All interface addresses
        for a in cls._get_all_addresses(
            mo_id,
            trap=bool(r["trap"]) and trap_source_type == "a",
            syslog=bool(r["syslog"]) and syslog_source_type == "a",
            ping=bool(r["ping"]),
        ):
            if a["address"] in addresses:
                continue
            addresses[a["address"]] = a
        # if not r["addresses"]:
        #    raise KeyError("No interfaces with IP")
        if not addresses:
            raise KeyError(f"Unsupported Trap Source Type: {trap_source_type}")
        r["addresses"] = list(addresses.values())
        return r

    @classmethod
    def _get_loopback_addresses(
        cls, mo_id, syslog: bool = True, trap: bool = True, ping: bool = True
    ) -> List[Dict[str, str]]:
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        # Get all loopbacks
        if_ids = {}
        for d in Interface._get_collection().find(
            {"managed_object": int(mo_id), "type": "loopback"}, {"_id": 1, "name": 1}
        ):
            if_ids[d["_id"]] = d["name"]
        if not if_ids:
            return []
        # Get loopback's addresses
        r = []
        for d in SubInterface._get_collection().find(
            {
                "managed_object": int(mo_id),
                "interface": {"$in": list(if_ids)},
                "ipv4_addresses": {"$exists": True},
            },
            {"_id": 0, "ipv4_addresses": 1, "interface": 1},
        ):
            for a in d.get("ipv4_addresses", []):
                ip = IP.prefix(a)
                if ip.is_internal:
                    continue
                r += [
                    {
                        "address": str(ip.address),
                        "is_fatal": False,
                        "interface": if_ids[d["interface"]],
                        "syslog_source": syslog,
                        "trap_source": trap,
                        "ping_check": ping,
                    }
                ]
        return r

    @classmethod
    def _get_all_addresses(cls, mo_id, syslog: bool = True, trap: bool = True, ping: bool = True):
        from noc.inv.models.subinterface import SubInterface

        r = []
        for d in SubInterface._get_collection().find(
            {"managed_object": int(mo_id), "ipv4_addresses": {"$exists": True}},
            {"ipv4_addresses": 1, "interface": 1},
        ):
            for a in d.get("ipv4_addresses", []):
                ip = IP.prefix(a)
                if ip.is_internal:
                    continue
                r += [
                    {
                        "address": str(ip.address),
                        "is_fatal": False,
                        "interface": str(d["interface"]),
                        "syslog_source": syslog,
                        "trap_source": trap,
                        "ping_check": ping,
                    }
                ]
        return r

    @classmethod
    def get_meta(cls, data):
        return {"pool": data.get("pool")}

    @classmethod
    def filter_pool(cls, name):
        return {f"{cls.F_META}.pool": name}
