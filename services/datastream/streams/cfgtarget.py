# ----------------------------------------------------------------------
# cfgtrap datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Optional, Any, Iterable, Tuple
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

    @property
    def opaque_data(self):
        """
        ManagedObject Opaque Data
        :return:
        """
        r = {
            "id": str(self.mo_id),
            "bi_id": str(self.bi_id),
            "name": self.name,
            "administrative_domain": {"id": self.adm_domain, "name": self.adm_domain_name},
            "labels": [
                DataStream.qs(ll)
                for ll in Label.objects.filter(
                    name__in=self.labels, expose_datastream=True
                ).values_list("name")
            ],
        }
        if self.remote_system:
            rs = RemoteSystem.get_by_id(self.remote_system)
            r["remote_system"] = {"id": str(rs.id), "name": rs.name}
            r["remote_id"] = self.remote_id
        if self.adm_domain_remote_system:
            rs = RemoteSystem.get_by_id(self.adm_domain_remote_system)
            r["administrative_domain"]["remote_system"] = {
                "id": str(rs.id),
                "name": rs.name,
            }
            r["administrative_domain"]["remote_id"] = self.adm_domain_remote_id
        return r

    def enable_syslog_source(self, source: str) -> bool:
        """
        Check syslog source is enabled
        :param source:
        :return:
        """
        if source == "s" and not self.syslog_source_ip:
            return False
        if self.syslog_source_type == "a":
            return True
        return self.syslog_source_type == source

    def enable_snmptrap_source(self, source: str) -> bool:
        """
        Check SNMP Trap source is enabled
        :param source:
        :return:
        """
        if source == "s" and not self.trap_source_ip:
            return False
        if self.trap_source_type == "a":
            return True
        return self.trap_source_type == source

    def get_syslog_archive_policy(self):
        if self.syslog_archive_policy == "P":
            return str(self.mop_syslog_archive_policy)
        return str(self.syslog_archive_policy)

    @property
    def is_process_event(self) -> bool:
        """
        Get effective event processing policy
        :return:
        """
        if (
            str(self.event_processing_policy) == "P"
            and str(self.mop_event_processing_policy) == "E"
        ):
            return True
        elif str(self.event_processing_policy) == "E":
            return True
        return False

    @property
    def is_enable_ping(self) -> bool:
        return self.enable_ping and self.ping_interval and self.ping_interval > 0

    def get_ping_settings(self) -> Optional[Dict[str, Any]]:
        if not self.is_enable_ping:
            return None
        return {
            "interval": self.ping_interval,
            "policy": self.ping_policy,
            "size": self.ping_size,
            "count": self.ping_count,
            "timeout": self.ping_timeout_ms,
            "expr_policy": self.ping_time_expr_policy,
            "report_rtt": self.report_ping_rtt,
            "report_attempts": self.report_ping_attempts,
        }

    def get_syslog_settings(self) -> Optional[Dict[str, Any]]:
        """
        Get effective event archiving policy
        :return:
        """
        if self.syslog_source_type == "d" or not self.is_process_event:
            return None
        return {"archive_events": self.get_syslog_archive_policy()}

    def get_snmptrap_settings(self) -> Optional[Dict[str, Any]]:
        if self.trap_source_type == "d" or not self.is_process_event:
            return None
        return {
            "community": self.trap_community,
            "storm_policy": self.mop_trapcollector_storm_policy,
            "storm_threshold": self.mop_trapcollector_storm_threshold,
        }


class CfgTrapDataStream(DataStream):
    name = "cfgtarget"
    DIAGNOSTIC = SNMPTRAP_DIAG  # !!
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
        # Process event policy
        state = State.get_by_id(state)
        # Check if object capable to receive syslog events
        if not state.is_enabled_interaction("EVENT"):
            raise KeyError("Disabled by processed event by State")
        target = Target(*mo[0])
        # Process sources
        pool = str(Pool.get_by_id(pool).name)
        r = {
            "id": str(mo_id),
            "pool": pool,
            "fm_pool": str(Pool.get_by_id(fm_pool).name) if fm_pool else pool,
            "name": name,
            "bi_id": bi_id,
            "process_events": target.is_process_event,
            "effective_labels": effective_labels,
            "addresses": [],
            "opaque_data": target.opaque_data,
            "syslog": target.get_syslog_settings(),
            "trap": target.get_snmptrap_settings(),
            "ping": target.get_ping_settings(),
        }
        # Ping Settings
        if time_pattern:
            r["time_expr"] = TimePattern.get_code(time_pattern)
        if not (bool(r["ping"]) or bool(r["syslog"]) or bool(r["trap"])):
            raise KeyError("Not enable collectors")
        addresses = {}
        # Process sources
        if address and (
            target.enable_syslog_source("m")
            or target.enable_snmptrap_source("m")
            or target.is_enable_ping
        ):
            addresses[address] = {
                "address": address,
                "is_fatal": True,
                "interface": None,
                "syslog_source": target.enable_syslog_source("m"),
                "trap_source": target.enable_snmptrap_source("m"),
                "ping_check": target.is_enable_ping,
            }
        if target.enable_syslog_source("l") or target.enable_snmptrap_source("l"):
            for addr, ifname, source in cls._iter_addresses(mo_id):
                if addr in addresses:
                    # Skip Mgmt address
                    continue
                addresses[addr] = {
                    "address": addr,
                    "is_fatal": False,
                    "interface": ifname,
                    "syslog_source": target.enable_syslog_source(source),
                    "trap_source": target.enable_snmptrap_source(source),
                    "ping_check": False,
                }
        if target.enable_syslog_source("s") and target.syslog_source_ip not in addresses:
            addresses[target.syslog_source_ip] = {
                "address": str(target.syslog_source_ip),
                "is_fatal": False,
                "interface": None,
                "syslog_source": False,
                "trap_source": True,
                "ping_check": False,
            }
        if target.enable_snmptrap_source("s") and target.trap_source_ip not in addresses:
            addresses[target.trap_source_ip] = {
                "address": str(target.trap_source_ip),
                "is_fatal": False,
                "interface": None,
                "syslog_source": False,
                "trap_source": True,
                "ping_check": False,
            }
        if not addresses:
            raise KeyError(f"Unsupported Trap Source Type: {trap_source_type}")
        r["addresses"] = list(addresses.values())
        return r

    @classmethod
    def _iter_addresses(cls, mo_id) -> Iterable[Tuple[str, Optional[str], str]]:
        """
        Iterate over ManagedObject available addresses
        :return:
        """
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        # Get all interfaces
        if_ids = {}
        for d in Interface._get_collection().find(
            {"managed_object": int(mo_id)}, {"_id": 1, "name": 1, "type": 1}
        ):
            if_ids[str(d["_id"])] = (d["name"], d["type"])

        for d in SubInterface._get_collection().find(
            {"managed_object": int(mo_id), "ipv4_addresses": {"$exists": True}},
            {"ipv4_addresses": 1, "interface": 1},
        ):
            for a in d.get("ipv4_addresses", []):
                ip = IP.prefix(a)
                if ip.is_internal:
                    continue
                if_name, if_type = if_ids.get(str(d["interface"]), (None, None))
                yield str(ip.address), if_name, "l" if if_type == "loopback" else "a"

    @classmethod
    def get_meta(cls, data):
        r = {
            "collectors": [c for c in ["ping", "syslog", "trap"] if data.get(c)],
            "pool": data.get("pool"),
        }
        return r

    @classmethod
    def filter_pool(cls, name):
        return {f"{cls.F_META}.pool": name}

    @classmethod
    def filter_collector(cls, name: str):
        return {f"{cls.F_META}.collectors": {"$elemMatch": {"$elemMatch": {"$in": [name]}}}}
