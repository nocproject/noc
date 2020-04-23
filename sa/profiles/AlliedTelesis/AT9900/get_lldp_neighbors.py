# ---------------------------------------------------------------------
# AlliedTelesis.AT9900.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "AlliedTelesis.AT9900.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^\s+lldpRemLocalPortNum \S+ (?P<local_port_num>\S+)\n"
        r"^\s+lldpRemIndex \S+ (?P<index>\S+)\n"
        r"^\s+lldpRemTimeMark.+\n"
        r"^\s+lldpRemChassisIdSubtype \S+ (?P<chassis_id_subtype>\S+)\n"
        r"^\s+lldpRemChassisId \S+ (?P<chassis_id>\S+)\n"
        r"^\s+lldpRemPortIdSubtype \S+ (?P<port_id_subtype>\S+)\n"
        r"^\s+lldpRemPortId \S+ (?P<port_id>\S+)\n"
        r"^\s+lldpRemPortDesc \S+ (?P<port_description>((.+\n)?^\s+\d.+)|.+)\n"
        r"^\s+lldpRemSysName \S+ (?P<system_name>\S+)\n"
        r"^\s+lldpRemSysDesc \S+ (?P<system_description>((.+\n)?^\s+\d.+)|.+)\n"
        r"^\s+lldpRemSysCapSupported \S+ (?P<cap_support>.+)\n"
        r"^\s+lldpRemSysCapEnabled \S+ (?P<caps>.+)\n",
        re.MULTILINE | re.IGNORECASE,
    )

    def execute_cli(self):
        r = []
        v = self.cli("show lldp neighbour detail")
        for match in self.rx_lldp.finditer(v):
            local_port = "port" + match.group("local_port_num").strip()
            iface = {"local_interface": local_port, "neighbors": []}
            cap = lldp_caps_to_bits(
                match.group("caps").strip().split(","),
                {
                    "Other": LLDP_CAP_OTHER,
                    "Repeater": LLDP_CAP_REPEATER,
                    "Bridge": LLDP_CAP_BRIDGE,
                    "Access Point": LLDP_CAP_WLAN_ACCESS_POINT,
                    "Router": LLDP_CAP_ROUTER,
                    "Telephone": LLDP_CAP_TELEPHONE,
                    "D": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "Station only": LLDP_CAP_STATION_ONLY,
                },
            )
            n = {
                "remote_chassis_id": match.group("chassis_id").strip(),
                "remote_chassis_id_subtype": match.group("chassis_id_subtype").strip(),
                "remote_port": match.group("port_id").strip(),
                "remote_port_subtype": match.group("port_id_subtype").strip(),
                "remote_capabilities": cap,
            }
            system_name = match.group("system_name").strip()
            if system_name and system_name != "-":
                n["remote_system_name"] = system_name
            system_description = match.group("system_description").strip()
            if system_description and system_description != "-":
                n["remote_system_description"] = re.sub(r"\s+", " ", system_description)
            port_description = match.group("port_description").strip()
            if port_description and port_description != "-":
                n["remote_port_description"] = re.sub(r"\s+", " ", port_description)
            iface["neighbors"] += [n]
            r += [iface]
        return r
