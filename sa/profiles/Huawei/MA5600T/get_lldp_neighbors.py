# ---------------------------------------------------------------------
# Huawei.MA5600T.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors, MACAddressParameter
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Huawei.MA5600T.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    always_prefer = "S"

    # ethernet0/2/0     -              1/0/26                        120
    rx_iface_sep = re.compile(r"^\s*[a-z]+(?P<iface>\d/\d/\d)\s+", re.MULTILINE)

    CHASSIS_TYPES = {
        "chassiscomponent": 1,
        "chassis component": 1,
        "portcomponent": 3,
        "port component": 3,
        "macaddress": 4,
        "mac address": 4,
        "networkaddress": 5,
        "network address": 5,
        "interfacename": 6,
        "interface name": 6,
        "local": 7,
        "locally assigned": 7,
    }

    PORT_TYPES = {
        "interfacealias": 1,
        "interface alias": 1,
        "portcomponent": 2,
        "port component": 2,
        "macaddress": 3,
        "mac address": 3,
        "interfacename": 5,
        "interface name": 5,
        "local": 7,
        "locally assigned": 7,
    }

    CAPS = {
        "-": 0,
        "--": 0,
        "na": 0,
        "other": 1,
        "repeater": 2,
        "bridge": 4,
        "wlan": 8,
        "wlanaccesspoint": 8,
        "access point": 8,
        "router": 16,
        "telephone": 32,
        "cable": 64,
        "docsiscabledevice": 64,
        "station": 128,
        "stationonly": 128,
    }

    def execute_cli(self, **kwargs):
        r = []
        try:
            v = self.cli("display lldp neighbor brief")
        except self.CLISyntaxError:
            raise NotImplementedError
        il = self.rx_iface_sep.findall(v)
        if not il:
            return r
        for local_iface in il:
            neighbors = []
            ne = self.cli("display lldp neighbor port %s" % local_iface)
            n = parse_kv(
                {
                    "chassisid subtype": "remote_chassis_id_subtype",
                    "chassisid": "remote_chassis_id",
                    "portid subtype": "remote_port_subtype",
                    "portid": "remote_port",
                    "port description": "remote_port_description",
                    "system capabilities enabled": "remote_capabilities",
                    "system name": "remote_system_name",
                    "system description": "remote_system_description",
                },
                ne,
            )
            # Convert chassis id
            n["remote_chassis_id_subtype"] = self.CHASSIS_TYPES[
                n["remote_chassis_id_subtype"].lower()
            ]

            if n["remote_chassis_id_subtype"] == 3:
                n["remote_chassis_id"] = MACAddressParameter().clean(n["remote_chassis_id"])
            # Convert port id
            n["remote_port_subtype"] = self.PORT_TYPES[n["remote_port_subtype"].lower()]
            if n["remote_port_subtype"] == 3:
                n["remote_port"] = MACAddressParameter().clean(n["remote_port"])
            if n.get("remote_port_description") in ["-", "NA", "N/A"]:
                del n["remote_port_description"]
            if n.get("remote_system_description") in ["-", "NA", "N/A"]:
                del n["remote_system_description"]
            if n.get("remote_system_name") in ["-", "NA", "N/A"]:
                del n["remote_system_name"]
            # Process capabilities
            caps = 0
            cs = n.get("remote_capabilities", "").replace(",", " ")
            for c in cs.split():
                caps |= self.CAPS[c.lower().strip()]
            n["remote_capabilities"] = caps
            neighbors += [n]
            if neighbors:
                r += [{"local_interface": local_iface, "neighbors": neighbors}]
        return r
