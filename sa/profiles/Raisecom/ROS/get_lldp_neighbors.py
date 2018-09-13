# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.lib.validators import is_ipv4, is_ipv6, is_mac


class Script(BaseScript):
    name = "Raisecom.ROS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^\s*(?:Port\s+)?(port)?(?P<port>gigaethernet1/1/\d+|\d+)\s*has\s+1\s*remotes:\s*\n(?:\n)?"
        r"^\s*Remote\s*1\s*\n"
        r"^\s*\-+\n"
        r"^\s*ChassisIdSubtype:\s+(?P<ch_type>\S+)\s*\n"
        r"^\s*ChassisId:\s+(?P<ch_id>\S+)\s*\n"
        r"^\s*PortIdSubtype:\s+(?P<port_id_subtype>\S+)\s*\n"
        r"^\s*PortId:\s+(?P<port_id>.+)\s*\n"
        r"^\s*PortDesc:\s+(?P<port_descr>(.+\n)+)"
        r"^\s*SysName:\s+(?P<sys_name>.+)\s*\n"
        r"^\s*SysDesc:\s+(?P<sys_descr>(.+\n)+)"
        r"^\s*SysCapSupported:\s+(?P<sys_caps_supported>\S+)\s*\n"
        r"^\s*SysCapEnabled:\s+(?P<sys_caps_enabled>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)

    rx_lldp_womac = re.compile(
        r"^\s*(?:Port\s+)?(port)?(?P<port>gigaethernet1/1/\d+|\d+)\s*has\s+1\s*remotes:\s*\n(?:\n)?"
        r"^\s*Remote\s*1\s*\n"
        r"^\s*\-+\n"
        r"^\s*ChassisIdSubtype\s*:\s+(?P<ch_type>\S+)\s*\n"
        r"^\s*PortIdSubtype\s*:\s+(?P<port_id_subtype>\S+)\s*\n"
        r"^\s*PortId\s*:\s+(?P<port_id>.+)\s*\n"
        r"^\s*PortDesc\s*:\s+(?P<port_descr>(.+\n)+)"
        r"^\s*SysName\s*:\s+(?P<sys_name>.+)\s*\n"
        r"^\s*SysDesc\s*:\s+(?P<sys_descr>(.+\n)+)"
        r"^\s*SysCapSupported\s*:\s+(?P<sys_caps_supported>\S+)\s*\n"
        r"^\s*SysCapEnabled\s*:\s+(?P<sys_caps_enabled>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)

    rx_lldp_rem = re.compile(
        r"^port(?P<port>\d+)\s+(?P<ch_id>\S+)", re.MULTILINE)

    def execute_cli(self):
        r = []
        r_rem = []
        v = self.cli("show lldp remote")
        for match in self.rx_lldp_rem.finditer(v):
            chassis_id = match.group("ch_id")
            if is_ipv4(chassis_id) or is_ipv6(chassis_id):
                chassis_id_subtype = 5
            elif is_mac(chassis_id):
                chassis_id_subtype = 4
            else:
                chassis_id_subtype = 7
            r_rem += [{
                "local_interface": match.group("port"),
                "remote_chassis_id": chassis_id,
                "remote_chassis_id_subtype": chassis_id_subtype
            }]
        v = self.cli("show lldp remote detail")
        # If detail command not contain ch id
        ext_ch_id = False
        lldp_iter = list(self.rx_lldp.finditer(v))
        if not lldp_iter:
            ext_ch_id = True
            lldp_iter = list(self.rx_lldp_womac.finditer(v))
            self.logger.debug("Not Find MAC in re")
        for match in lldp_iter:
            i = {"local_interface": match.group("port"), "neighbors": []}
            cap = 0
            for c in match.group("sys_caps_enabled").strip().split(","):
                cap |= {
                    "N/A": 0,
                    "Other": 1,
                    "Repeater/Hub": 2,
                    "Bridge/Switch": 4,
                    "Router": 16,
                    "Telephone": 32,
                    "Station": 128
                }[c]
            n = {
                "remote_chassis_id_subtype": {
                    "macAddress": 4,
                    "networkAddress": 5
                }[match.group("ch_type")],
                "remote_chassis_id": match.group("ch_id") if not ext_ch_id else None,
                "remote_port_subtype": {
                    "ifAlias": 1,
                    "macAddress": 3,
                    "ifName": 5,
                    "portComponent": 5,
                    "local": 7
                }[match.group("port_id_subtype")],
                "remote_port": match.group("port_id"),
                "remote_capabilities": cap
            }
            if match.group("sys_name").strip() != "N/A":
                n["remote_system_name"] = match.group("sys_name").strip()
            if match.group("sys_descr").strip() != "N/A":
                sd = match.group("sys_descr").strip()
                if "SysDesc:" in sd:
                    sd = sd.split()[-1]
                n["remote_system_description"] = re.sub("\n\s{29,30}", "", sd)
            if match.group("port_descr").strip() != "N/A":
                n["remote_port_description"] = \
                    re.sub("\n\s{29,30}", "", match.group("port_descr").strip())
                match.group("port_descr")
            if n["remote_chassis_id"] is None:
                for j in r_rem:
                    if i["local_interface"] == j["local_interface"]:
                        n["remote_chassis_id"] = j["remote_chassis_id"]
                        n["remote_chassis_id_subtype"] = \
                            j["remote_chassis_id_subtype"]
                        break
            i["neighbors"] += [n]
            r += [i]
        return r
