# ----------------------------------------------------------------------
# Generic.get_bgp_peer_status.py script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Optional

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetbgppeerstatus import IGetBGPPeerStatus
from noc.core.mib import mib
from noc.core.bgp import BGPState


class Script(BaseScript):
    name = "Generic.get_bgp_peer_status"
    interface = IGetBGPPeerStatus
    requires = []
    oid_map = {
        mib["BGP4-MIB::bgpPeerState"]: "status",
        mib["BGP4-MIB::bgpPeerAdminStatus"]: "admin_status",
        mib["BGP4-MIB::bgpPeerFsmEstablishedTime"]: "status_duration",
        mib["BGP4-MIB::bgpPeerLastError"]: "last_error",
    }

    def execute_snmp(self, peers, **kwargs):
        oids = []
        if not self.has_capability("SNMP | MIB | BGP4-MIB"):
            raise NotImplementedError("BGP-MIB not supported on Device Capabilities")
        for p in peers:
            oids += [
                mib["BGP4-MIB::bgpPeerState", p["peer"]],
                mib["BGP4-MIB::bgpPeerAdminStatus", p["peer"]],
                mib["BGP4-MIB::bgpPeerFsmEstablishedTime", p["peer"]],
                mib["BGP4-MIB::bgpPeerLastError", p["peer"]],
            ]
        if not oids:
            return []
        r = {}
        chunk = self.snmp.get_chunked(oids, chunk_size=10)
        for oid, v in chunk.items():
            oid, *peer = oid.rsplit(".", 4)
            if oid not in self.oid_map:
                self.logger.warning("Unknown oid: %s", oid)
                continue
            peer = ".".join(peer)
            key = self.oid_map[oid]
            if peer not in r:
                r[peer] = {"neighbor": peer}
            if key == "admin_status":
                v = v == 2
            elif key == "status":
                v = BGPState(v)
            r[peer][key] = v
        return list(r.values())
