# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Qtech.QSW.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_line = re.compile(
        r"^Interface Ethernet (?P<interface>\S+)\s*.Port\s+LLDP:\s+\S+\s+Pkt\s+Tx:\s+\d+\s+Pkt\s+Rx:\s+\d+\s*.Total neighbor count: \d+\s*.\s*.Neighbor \(\d+\):\s*.TTL: \d+\(s\)\s*.Chassis ID:\s+(?P<chassis_id>\S+)\s*.Port ID: port (?P<port_id>\S+)\s*.System Name: (?P<name>\S+)",
        re.DOTALL|re.MULTILINE)
    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute(self):
        r = []
        # Try SNMP first

        """
        # SNMP not working
        
        if self.has_snmp():
            try:

# lldpRemLocalPortNum
# lldpRemChassisIdSubtype lldpRemChassisId
# lldpRemPortIdSubtype lldpRemPortId
# lldpRemSysName lldpRemSysCapEnabled
                for v in self.snmp.get_tables(
                    ["1.0.8802.1.1.2.1.4.1.1.2",
                    "1.0.8802.1.1.2.1.4.1.1.4", "1.0.8802.1.1.2.1.4.1.1.5",
                    "1.0.8802.1.1.2.1.4.1.1.6", "1.0.8802.1.1.2.1.4.1.1.7",
                    "1.0.8802.1.1.2.1.4.1.1.9", "1.0.8802.1.1.2.1.4.1.1.12"
                    ], bulk=True):
                    local_interface = self.snmp.get(
                        "1.3.6.1.2.1.31.1.1.1.1." + v[1], cached=True)
                    remote_chassis_id_subtype = v[2]
                    remotechassisid = ":".join(["%02x" % ord(c) for c in v[3]])
                    remote_port_subtype = v[4]
                    if remote_port_subtype == 7:
                        remote_port_subtype = 5
                    remote_port = v[5]
                    remote_system_name = v[6]
                    remote_capabilities = v[7]

                    i = {"local_interface": local_interface, "neighbors": []}
                    n = {
                        "remote_chassis_id_subtype": remote_chassis_id_subtype,
                        "remote_chassis_id": remotechassisid,
                        "remote_port_subtype": remote_port_subtype,
                        "remote_port": remote_port,
                        "remote_capabilities": remote_capabilities,
                        }
                    if remote_system_name:
                        n["remote_system_name"] = remote_system_name
                    i["neighbors"].append(n)
                    r.append(i)
                return r

            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        try:
            lldp = self.cli("show lldp interface")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_line.finditer(lldp):
            local_interface = match.group("interface")
            local_interface = \
                self.profile.convert_interface_name(local_interface)
            remote_chassis_id = match.group("chassis_id")
            remote_port = match.group("port_id")
            remote_system_name = match.group("name")

            # Build neighbor data
            # Get capability
            cap = 0
#            for c in match.group("capabilities").split(","):
            if cap:
                c = c.strip()
                if c:
                    cap |= {
                        "O": 1, "r": 2, "B": 4,
                        "W": 8, "R": 16, "T": 32,
                        "C": 64, "S": 128, "D": 256,
                        "H": 512, "TP": 1024,
                    }[c]

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
#            n["remote_chassis_id_subtype"] = 4

            i["neighbors"].append(n)
            r.append(i)
        return r
