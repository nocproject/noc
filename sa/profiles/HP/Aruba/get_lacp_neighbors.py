# ---------------------------------------------------------------------
# HP.Aruba.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "HP.Aruba.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_system_id = re.compile(r"System-ID\s+:\s*(?P<system_id>\S+)")
    rx_actor_detail = re.compile(r"Actor details of all interfaces:")
    rx_partner_detail = re.compile(r"Partner details of all interfaces:")
    rx_row = re.compile(
        r"^(?P<lport>\S+)\s+(?P<lag>lag\d+)\S*\s+(?P<port_id>\d+)\s+(?P<port_pri>\d+)"
        r"\s+(?P<state>\S+)\s+(?P<system_id>\S+)\s+(?P<pri>\d+)\s+(?P<key>\d+).*",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        v = self.cli("show lacp configuration")
        sid = self.rx_system_id.search(v).group("system_id")
        v = self.cli("show lacp interfaces")
        a_match = self.rx_actor_detail.search(v)
        p_match = self.rx_partner_detail.search(v)
        if not p_match:
            # Neighbors not found
            return []
        p_map = {}
        m = {}
        for lport, lag, port_id, _, _, system_id, _, key in self.rx_row.findall(
            v[a_match.end() : p_match.start()]
        ):
            p_map[lport] = {"local_port_id": port_id, "system": system_id, "key": key}
        for lport, lag, port_id, _, _, system_id, _, key in self.rx_row.findall(v[p_match.end() :]):
            if system_id == "02:01:00:00:01:00":
                # Neighbors not found
                continue
            if lag not in m:
                m[lag] = {"lag_id": lag[3:], "interface": lag, "system_id": sid, "bundle": []}
            m[lag]["bundle"] += [
                {
                    "interface": lport,
                    "local_port_id": p_map[lport]["local_port_id"],
                    "remote_system_id": system_id,
                    "remote_port_id": port_id,
                }
            ]
        return list(m.values())
