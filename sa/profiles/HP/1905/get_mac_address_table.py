# ---------------------------------------------------------------------
# HP.1905.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.snmp.render import render_mac
from noc.core.mac import MAC


class Script(BaseScript):
    name = "HP.1905.get_mac_address_table"
    interface = IGetMACAddressTable
    cached = True

    def execute_snmp(self, interface=None, vlan=None, mac=None):
        r = []
        vlan_oid = []
        if mac is not None:
            mac = mac.lower()
        for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"], bulk=True):
            vlan_oid.append(v[0])
        # mac iface type
        for v in self.snmp.get_tables(
            ["1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2", "1.3.6.1.2.1.17.4.3.1.3"],
            bulk=True,
            display_hints={
                "1.3.6.1.2.1.17.4.3.1.3": render_mac,
            }
        ):
            if v[1]:
                chassis = MAC(v[1])
                if mac is not None:
                    if chassis == mac:
                        pass
                    else:
                        continue
            else:
                continue
            if not v[3]:
                continue
            if int(v[3]) > 3 or int(v[3]) < 1:
                continue
            # iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[2],
            #        cached=True)  # IF-MIB
            # if not iface:
            #    oid = "1.3.6.1.2.1.2.2.1.2." + v[2]
            #    i = self.snmp.get(oid, cached=True)
            if int(v[3]) < 25:
                iface = "Ethernet0/" + str(int(v[2]))
            else:
                iface = "Copper0/" + str(int(v[2]))
            if interface is not None:
                if iface == interface:
                    pass
                else:
                    continue
            for i in vlan_oid:
                if v[0] in i:
                    vlan_id = int(i.split(".")[0])
                    break
            if vlan is not None:
                if vlan_id == vlan:
                    pass
                else:
                    continue
            r.append(
                {
                    "interfaces": [iface],
                    "mac": chassis,
                    "type": {"3": "D", "2": "S", "1": "S"}[str(v[3])],
                    "vlan_id": vlan_id,
                }
            )
            return r
