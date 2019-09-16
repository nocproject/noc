# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
)
from noc.core.validators import is_mac


class Script(BaseScript):
    name = "Siklu.EH.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    CHASSIS_TYPES = {
        "macaddress": LLDP_CHASSIS_SUBTYPE_MAC,
        "mac address": LLDP_CHASSIS_SUBTYPE_MAC,
        "mac-addr": LLDP_CHASSIS_SUBTYPE_MAC,
        "network-addr": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "interfacename": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
        "interface name": LLDP_CHASSIS_SUBTYPE_INTERFACE_NAME,
        "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
    }

    PORT_TYPES = {
        "interfacealias": LLDP_PORT_SUBTYPE_ALIAS,
        "interface alias": LLDP_PORT_SUBTYPE_ALIAS,
        "interface-alias": LLDP_PORT_SUBTYPE_ALIAS,
        "macaddress": LLDP_PORT_SUBTYPE_MAC,
        "mac address": LLDP_PORT_SUBTYPE_MAC,
        "mac-addr": LLDP_PORT_SUBTYPE_MAC,
        "interfacename": LLDP_PORT_SUBTYPE_NAME,
        "interface-name": LLDP_PORT_SUBTYPE_NAME,
        "interface name": LLDP_PORT_SUBTYPE_NAME,
        "local": LLDP_PORT_SUBTYPE_LOCAL,
    }

    rx_ecfg = re.compile(
        r"^(?P<cmd>\S+)\s+(?P<name>\S+)\s+\d+\s+(?P<key>\S+)\s*:(?P<value>.*?)$", re.MULTILINE
    )

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
            if not section.strip():
                continue
            name, cfg = self.parse_section(section)
            # Hack. We use port_id for chassis_id
            if "port-id" not in cfg:
                r += [{"local_interface": name, "neighbors": []}]
                return r
            remote_chassis_id = cfg["chassis-id"]
            remote_chassis_type = self.CHASSIS_TYPES[cfg["chassis-id-subtype"]]
            if cfg["chassis-id-subtype"] == "network-addr" and is_mac(cfg["port-id"]):
                # Network address is default 192.168.0.1
                remote_chassis_id = cfg["port-id"]
                remote_chassis_type = LLDP_CHASSIS_SUBTYPE_MAC
            neighbor = {
                "remote_chassis_id": remote_chassis_id,
                "remote_chassis_id_subtype": remote_chassis_type,
                "remote_port": cfg["port-id"],
                "remote_port_subtype": self.PORT_TYPES[cfg["port-id-subtype"]],
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
                r += [{"local_interface": name, "neighbors": [neighbor]}]
        return r
