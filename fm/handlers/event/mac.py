# ---------------------------------------------------------------------
# MAC handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from time import perf_counter_ns
from typing import Any

# Third-party modules
from bson import ObjectId
from cachetools import TTLCache, cached

# NOC modules
from noc.core.fm.event import Event
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.service.loader import get_service
from noc.core.mac import MAC

NS = 1_000_000_000
IF_PROFILE_TTL_NS = 60 * NS
MO_TTL_NS = 60 * NS
MO_CACHE_SIZE = 1_000
MO_CACHE_TTL = 60


def register(event: Event, managed_object: ManagedObject) -> None:
    """
    Register MAC from event.
    """
    vlan = int(event.vars.get("vlan", "0"))
    interface: str | None = Event.vars.get("interface")
    mac: str | None = Event.vars.get("mac")
    if not interface or not mac:
        return
    # Resolve interface
    mo_ifaces = get_mo_iterfaces(managed_object.id)
    if not mo_ifaces:
        return
    if_profile = mo_ifaces.get(interface)
    if not if_profile:
        return
    # Spool data
    ts = event.timestamp
    svc = get_service()
    svc.register_metrics(
        "mac",
        [
            {
                "date": ts.strftime("%Y-%m-%d"),
                "ts": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "managed_object": managed_object.bi_id,
                "mac": int(MAC(mac)),
                "interface": interface,
                "interface_profile": if_profile.interface_profile,
                "segment": managed_object.segment.bi_id,
                "vlan": vlan,
                "is_uni": if_profile.is_uni,
            }
        ],
    )


@dataclass
class IfProfile(object):
    """
    Interface profile settings.

    Arguments:
        interface_profile: Interface profile BI ID.
        is_uni: UNI flag.
    """

    interface_profile: int
    is_uni: int

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "IfProfile":
        """Create item from data dict."""
        return IfProfile(interface_profile=data["bi_id"], is_uni=1 if data["is_uni"] else 0)


class IfProfileMap(object):
    def __init__(self):
        self.map: dict[ObjectId, IfProfile] = {}
        self.last_update = perf_counter_ns() - IF_PROFILE_TTL_NS

    def refresh(self) -> None:
        """
        Refresh cache when necessary
        """
        ts = perf_counter_ns()
        if ts - self.last_update < IF_PROFILE_TTL_NS:
            return
        # Reload data
        coll = InterfaceProfile._get_collection()
        r = {}
        for doc in coll.find({}, {"_id": 1, "bi_id": 1, "is_uni": 1}):
            r[doc["_id"]] = IfProfile.from_json(doc)
        self.last_update = ts
        self.map = r


@cached(TTLCache(maxsize=MO_CACHE_SIZE, ttl=MO_CACHE_TTL))
def get_mo_iterfaces(mo_id: int) -> dict[str, IfProfile]:
    coll = Interface._get_collection()
    r: dict[str, IfProfile] = {}
    if_profile_map.refresh()
    for doc in coll.find({"managed_object": mo_id}, {"_id": 0, "name": 1, "profile": 1}):
        name = doc.get("name")
        profile = doc.get("profile")
        if not name or not profile:
            continue
        profile = if_profile_map.map.get(profile)
        if profile:
            r[name] = profile
    return r


# Singletones
if_profile_map = IfProfileMap()
