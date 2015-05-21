# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4
##
## @todo: SNMP Support
##


class Script(NOCScript):
    name = "Extreme.XOS.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_lldp_nei = re.compile(r"^(?P<interface>\d+)\s+(?P<chassis_id>\S+)\s+(?P<port_id>\S+)\s+\d+\s+\d+",  re.DOTALL|re.MULTILINE)
    rx_edp_nei = re.compile(r"^(?P<interface>\d+)\s+(?P<name>\S+)\s+[0-9a-f]{2}:[0-9a-f]{2}:(?P<chassis_id>\S+)\s+\d:(?P<port_id>\d+)\s+\d+\s+\d+",  re.DOTALL|re.MULTILINE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

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

            i = {"local_interface": local_interface, "neighbors": []}
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
                }
            # TODO:
            n["remote_chassis_id_subtype"] = 4

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
