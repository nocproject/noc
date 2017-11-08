# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Siklu.EH.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    CHASSIS_TYPES = {
        "macaddress": 4,
        "mac address": 4,
        "mac-addr": 4,
        "network-addr": 4,
        "interfacename": 6,
        "interface name": 6,
        "local": 7
    }

    PORT_TYPES = {
        "interfacealias": 1,
        "interface alias": 1,
        "macaddress": 3,
        "mac address": 3,
        "mac-addr": 3,
        "interfacename": 5,
        "interface-name": 5,
        "interface name": 5,
        "local": 7
    }

    rx_ecfg = re.compile(
        r"^(?P<cmd>\S+)\s+(?P<name>\S+)\s+\d+\s+(?P<key>\S+)\s*:(?P<value>.*?)$",
        re.MULTILINE)

    def parse_section(self, section):
        r = {}
        name = None
        for match in self.rx_ecfg.finditer(section):
            name = match.group("name")
            r[match.group("key")] = match.group("value").strip()
        return name, r

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp-remote")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for section in v.split("\n\n"):
            if not section:
                continue
            name, cfg = self.parse_section(section)
            # Hack. We use port_id for chassis_id
            if "port-id" not in cfg:
                r += [{
                    "local_interface": name,
                    "neighbors": []
                }]
                return r
            neighbor = {
                "remote_chassis_id": cfg["port-id"],
                "remote_chassis_id_subtype": self.CHASSIS_TYPES[cfg["chassis-id-subtype"]],
                "remote_port": cfg["port-id"],
                "remote_port_subtype": self.PORT_TYPES[cfg["port-id-subtype"]]
            }
            if "port-descr" in cfg:
                neighbor["remote_port_description"] = cfg["port-descr"]
            if "sys-name" in cfg:
                neighbor["remote_system_name"] = cfg["sys-name"]
            if "sys-descr" in cfg:
                neighbor["remote_system_description"] = cfg["sys-descr"]
            found = False
            for i in r:
                if i["local_interface"] == name:
                    i["neighbors"] += [neighbor]
                    found = True
                    break
            if not found:
                r += [{
                    "local_interface": name,
                    "neighbors": [neighbor]
                }]
        return r
