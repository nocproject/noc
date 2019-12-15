# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.ZyNOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_int, is_ipv4, is_mac

# Python standard modules
import re


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_summary_split = re.compile(r"^LocalPort.+?\n", re.MULTILINE | re.IGNORECASE)
    rx_s_line = re.compile(r"(?P<local_if>\d+)\s+[0-9a-f:]+\s+.+?$")
    rx_remote_port = re.compile(r"^\s*Port id:(?P<remote_if>.*)", re.MULTILINE | re.IGNORECASE)
    rx_remote_port_desc = re.compile(
        r"^\s*Port Description:(?P<remote_if_desc>.*)", re.MULTILINE | re.IGNORECASE
    )
    rx_remote_port_subtype = re.compile(
        r"^\s*Port id subtype:(?P<remote_if_subtype>.*)", re.MULTILINE | re.IGNORECASE
    )
    rx_chassis_id = re.compile(r"^\s*Chassis id:\s*(?P<id>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_enabled_caps = re.compile(
        r"^\s*System Capabilities Enabled:\s*"
        r"(?P<caps>((other|repeater|bridge|router|wlan-access-point"
        r"|telephone|docsis-cable-device|station-only)\s+)+)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_system = re.compile(r"^\s*System Name:\s*(?P<name>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_system_desc = re.compile(
        r"^\s*System Description:\s*(?P<desc>.*)", re.MULTILINE | re.IGNORECASE
    )

    def execute(self):
        r = []
        try:
            v = self.cli("sh lldp info remote")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        v = self.rx_summary_split.split(v)[1]
        lldp_interfaces = []

        # Get lldp interfaces
        for line in v.splitlines():
            line = line.strip()
            if not line:
                break
            match = self.rx_s_line.match(line)
            if not match:
                continue
            lldp_interfaces += [match.group("local_if")]

        # Get lldp neighbors
        for local_if in lldp_interfaces:
            i = {"local_interface": local_if, "neighbors": []}

            # Get neighbor details
            try:
                v = self.cli("sh lldp info remote interface port-channel %s" % local_if)
            except self.CLISyntaxError:
                raise self.NotSupportedError()

            # Get remote port
            match = self.re_search(self.rx_remote_port, v)
            remote_port = match.group("remote_if").strip()

            # match = self.re_search(self.rx_remote_port_desc, v)
            match = self.rx_remote_port_desc.search(v)
            if match:
                remote_port_desc = match.group("remote_if_desc").strip()
            else:
                remote_port_desc = ""

            match = self.rx_remote_port_subtype.search(v)
            if match:
                remote_port_subtype_str = match.group("remote_if_subtype").strip()
            else:
                remote_port_subtype_str = ""

            # Get remote port subtype from "Port ID Subtype" field
            if remote_port_subtype_str == "local-assigned":
                remote_port_subtype = 7  # Local
            else:
                remote_port_subtype = 5
                if is_ipv4(remote_port):
                    # Actually networkAddress(4)
                    remote_port_subtype = 4
                elif is_mac(remote_port):
                    # Actually macAddress(3)
                    remote_port_subtype = 3
                elif is_int(remote_port):
                    # Actually local(7)
                    remote_port_subtype = 7
                else:
                    remote_port_subtype = 128  # PORT_SUBTYPE_UNSPECIFIED
            n = {
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_chassis_id_subtype": 4,
            }
            if remote_port_desc:
                n["remote_port_description"] = remote_port_desc

            # Get Chassis ID
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"] = match.group("id")

            # Get capabilities
            cap = 0
            match = self.rx_enabled_caps.search(v)
            if match:
                for c in match.group("caps").split():
                    c = c.strip()
                    if c:
                        cap |= {
                            "other": 1,
                            "repeater": 2,
                            "bridge": 4,
                            "wlan-access-point": 8,
                            "router": 16,
                            "telephone": 32,
                            "docsis-cable-device": 64,
                            "station-only": 128,
                        }[c.lower()]
            n["remote_capabilities"] = cap

            # Get system name
            match = self.rx_system.search(v)
            if match:
                n["remote_system_name"] = match.group("name")
            match = self.rx_system_desc.search(v)
            if match:
                n["remote_system_description"] = match.group("desc")
            i["neighbors"] += [n]
            r += [i]
        return r
