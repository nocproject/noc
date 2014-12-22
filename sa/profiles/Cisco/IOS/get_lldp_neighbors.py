# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(NOCScript):
    name = "Cisco.IOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_summary_split = re.compile(r"^Device ID.+?\n",
                                  re.MULTILINE | re.IGNORECASE)
    rx_s_line = re.compile(
        r"^\S+\s*(?P<local_if>(?:Fa|Gi|Te)\d+[\d/\.]*)\s+.+$")
    rx_chassis_id = re.compile(r"^Chassis id:\s*(?P<id>\S+)",
        re.MULTILINE | re.IGNORECASE)
    rx_remote_port = re.compile("^Port id:\s*(?P<remote_if>.+?)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_enabled_caps = re.compile("^Enabled Capabilities:\s*(?P<caps>\S*)\s*$",
        re.MULTILINE | re.IGNORECASE)
    rx_system = re.compile(r"^System Name:\s*(?P<name>\S+)",
                           re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute(self):
        r = []
        try:
            v = self.cli("show lldp neighbors")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if v.startswith("%"):
            # % LLDP is not enabled
            return []
        v = self.rx_summary_split.split(v)[1]
        lldp_interfaces = []
        # Get LLDP interfaces with neighbors
        for l in v.splitlines():
            l = l.strip()
            if not l:
                break
            match = self.rx_s_line.match(l)
            if not match:
                continue
            lldp_interfaces += [match.group("local_if")]
        # Get LLDP neighbors
        for local_if in lldp_interfaces:
            i = {
                "local_interface": local_if,
                "neighbors": []
            }
            # Get neighbors details
            try:
                v = self.cli("show lldp neighbors %s detail" % local_if)
            except self.CLISyntaxError:
                # Found strange CLI syntax on Catalyst 4900
                # Allow ONLY interface name or "detail"
                # Need testing...
                raise self.NotSupportedError()
            # Get remote port
            match = self.re_search(self.rx_remote_port, v)
            remote_port = match.group("remote_if")
            remote_port_subtype = 128
            if self.rx_mac.match(remote_port):
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
            n = {
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
                "remote_chassis_id_subtype": 4
            }
            # Get chassis id
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            n["remote_chassis_id"] = match.group("id")
            # Get capabilities
            cap = 0
            match = self.rx_enabled_caps.search(v)
            if match:
                for c in match.group("caps").split(","):
                    c = c.strip()
                    if c:
                        cap |= {
                            "O": 1, "P": 2, "B": 4,
                            "W": 8, "R": 16, "T": 32,
                            "C": 64, "S": 128
                        }[c]
            n["remote_capabilities"] = cap
            # Get remote chassis id
            match = self.rx_system.search(v)
            if match:
                n["remote_system_name"] = match.group("name")
            i["neighbors"] += [n]
            r += [i]
        return r
