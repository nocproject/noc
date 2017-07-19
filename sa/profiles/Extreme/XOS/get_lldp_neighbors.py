# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4, is_mac
#
# @todo: SNMP Support
#


class Script(BaseScript):
    name = "Extreme.XOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp_nei = re.compile(
        r"^(?P<interface>\d+(\:\d+)?)\s+(?P<chassis_id>\S+)\s+"
        r"(?P<port_id>\S+)\s+\d+\s+\d+", re.DOTALL | re.MULTILINE)
    rx_edp_nei = re.compile(
        r"^(?P<interface>\d+(\:\d+)?)\s+(?P<name>\S+)\s+"
        r"[0-9a-f]{2}:[0-9a-f]{2}:(?P<chassis_id>\S+)\s+"
        r"\d:(?P<port_id>\d+)\s+\d+\s+\d+", re.DOTALL | re.MULTILINE)
    rx_lldp_detail = re.compile(
        r"^\s+- Chassis ID type\s*: (?P<chassis_id_subtype>.+)\n"
        r"^\s+Chassis ID\s*: (?P<chassis_id>\S+)\s*\n"
        r"^\s+- Port ID type\s*: (?P<port_id_subtype>.+)\n"
        r"^\s+Port ID\s*: (?P<port_id>\S+)\s*\n"
        r"^\s+- Time To Live: \d+ seconds\s*\n"
        r"^\s+- System Name: (?P<system_name>.+)\n"
        r"^\s+- System Description: (?P<system_descr>.+)\n"
        r"^\s+- System Capabilities : (?P<system_caps>.+)\n"
        r"^\s+Enabled Capabilities: (?P<enabled_caps>.+)\n"
        r"^\s+- Port Description: (?P<port_descr>.+)\n"
        r"^\s+- IEEE802.3 MAC/PHY Configuration/Status\s*\n",
        re.MULTILINE | re.DOTALL)
    chassis_types = {
        "MAC address (4)": 4,
        "Network address (5); Address type: IPv4 (1)": 5
    }
    port_types = {
        "MAC address (3)": 3,
        "ifName (5)": 5
    }

    def execute(self):
        r = []
        # Try SNMP first

        # Fallback to CLI
        # LLDP First
        try:
            lldp = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_lldp_nei.finditer(lldp):
            local_interface = match.group("interface")
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")

            # Build neighbor data
            # Get capability
            cap = 4
            # Get remote port subtype
            remote_port_subtype = 5
            if is_mac(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = 3
            elif is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = 4
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = 7

            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
                }
            # TODO:
            n["remote_chassis_id_subtype"] = 4
            try:
                c = self.cli(
                    "show lldp ports %s neighbors detailed" % local_interface
                )
                match = self.rx_lldp_detail.search(c)
                if match:
                    n["remote_port_description"] = match.group(
                        "port_descr"
                    ).replace("\"", "").strip()
                    n["remote_port_description"] = re.sub(
                        r"\\\n\s*", "", n["remote_port_description"]
                    )
                    n["remote_system_name"] = match.group(
                        "system_name"
                    ).replace("\"", "").strip()
                    n["remote_system_name"] = re.sub(
                        r"\\\n\s*", "", n["remote_system_name"]
                    )
                    n["remote_system_description"] = match.group(
                        "system_descr"
                    ).replace("\"", "").strip()
                    n["remote_system_description"] = re.sub(
                        r"\\\n\s*", "", n["remote_system_description"]
                    )
                    n["remote_port_subtype"] = self.port_types[
                        match.group("port_id_subtype").strip()
                    ]
                    n["remote_chassis_id_subtype"] = self.chassis_types[
                        match.group("chassis_id_subtype").strip()
                    ]
            except self.CLISyntaxError:
                pass

            i["neighbors"].append(n)
            r.append(i)
        # Try EDP Second
        try:
            lldp = self.cli("show edp ports all")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_edp_nei.finditer(lldp):
            local_interface = match.group("interface")
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")
            remote_system_name = match.group("name")

            # Build neighbor data
            # Get capability
            cap = 4
            # Get remote port subtype
            remote_port_subtype = 5
            if is_mac(remote_port):
                # Actually macAddress(3)
                # Convert MAC to common form
                remote_port = MACAddressParameter().clean(remote_port)
                remote_port_subtype = 3
            elif is_ipv4(remote_port):
                # Actually networkAddress(4)
                remote_port_subtype = 4
            elif is_int(remote_port):
                # Actually local(7)
                remote_port_subtype = 7

            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
                }
            if remote_system_name:
                n["remote_system_name"] = remote_system_name
            # TODO:
            n["remote_chassis_id_subtype"] = 4

            i["neighbors"].append(n)
            r.append(i)

        return r
