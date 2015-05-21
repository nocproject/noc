# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Eltex.MES.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    CAPS_MAP = {
        "O": 1, "r": 2, "B": 4,
        "W": 8, "R": 16, "T": 32,
        "C": 64, "S": 128, "D": 256,
        "H": 512, "TP": 1024,
    }

    def execute(self):
        r = []
        """
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # lldpRemLocalPortNum
                # lldpRemChassisIdSubtype lldpRemChassisId
                # lldpRemPortIdSubtype lldpRemPortId
                # lldpRemSysName lldpRemSysCapEnabled
                for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.4.1.1.2",
                                               "1.0.8802.1.1.2.1.4.1.1.4",
                                               "1.0.8802.1.1.2.1.4.1.1.5",
                                               "1.0.8802.1.1.2.1.4.1.1.6",
                                               "1.0.8802.1.1.2.1.4.1.1.7",
                                               "1.0.8802.1.1.2.1.4.1.1.9",
                                               "1.0.8802.1.1.2.1.4.1.1.12"
                                               ], bulk=True):
                    local_interface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." +
                                                    v[1], cached=True)
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
        lldp = self.cli("show lldp neighbors")
        for link in parse_table(lldp, allow_wrap=True):
            local_interface = link[0]
            remote_chassis_id = link[1]
            remote_port = link[2]
            remote_system_name = link[3]
            # Build neighbor data
            # Get capability
            cap = 0
            for c in link[4].split(","):
                c = c.strip()
                if c:
                    cap |= self.CAPS_MAP[c]

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
                remote_port_subtype = 5

            i = {
                "local_interface": local_interface,
                "neighbors": []
            }
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_port": remote_port,
                "remote_capabilities": cap,
                "remote_port_subtype": remote_port_subtype,
            }
            if remote_system_name:
                n["remote_system_name"] = remote_system_name
            # @todo:
            # n["remote_chassis_id_subtype"] = 4
            i["neighbors"] += [n]
            r += [i]
        return r
