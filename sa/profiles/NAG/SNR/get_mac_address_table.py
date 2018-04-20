# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# NAG.SNR.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "NAG.SNR.get_mac_address_table"
    interface = IGetMACAddressTable
=======
##----------------------------------------------------------------------
## NAG.SNR.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "NAG.SNR.get_mac_address_table"
    implements = [IGetMACAddressTable]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cached = True

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                vlan_oid = []
                if mac is not None:
                    mac = mac.lower()
<<<<<<< HEAD
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"], bulk=True):
                        vlan_oid.append(v[0])
                # mac iface type
                for v in self.snmp.get_tables(
                        ["1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2", "1.3.6.1.2.1.17.4.3.1.3"], bulk=True):
=======
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.2.2.1.2"],
                        bulk=True):
                        vlan_oid.append(v[0])
                # mac iface type
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.4.3.1.1", "1.3.6.1.2.1.17.4.3.1.2",
                    "1.3.6.1.2.1.17.4.3.1.3"], bulk=True):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if v[1]:
                        chassis = ":".join(["%02x" % ord(c) for c in v[1]])
                        if mac is not None:
                            if chassis == mac:
                                pass
                            else:
                                continue
                    else:
                        continue
                    if int(v[3]) > 3 or int(v[3]) < 1:
                        continue
<<<<<<< HEAD
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + str(v[2]), cached=True)  # IF-MIB
=======
                    iface = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1." + v[2],
                            cached=True)  # IF-MIB
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    if interface is not None:
                        if iface == interface:
                            pass
                        else:
                            continue
                    for i in vlan_oid:
                        if v[0] in i:
                            vlan_id = int(i.split('.')[0])
                            break
                    if vlan is not None:
                        if vlan_id == vlan:
                            pass
                        else:
                            continue

                    r.append({
                        "interfaces": [iface],
                        "mac": chassis,
<<<<<<< HEAD
                        "type": {"3": "D", "2": "S", "1": "S"}[str(v[3])],
=======
                        "type": {"3": "D", "2": "S", "1": "S"}[v[3]],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                        "vlan_id": vlan_id,
                        })
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        raise Exception("Not implemented")
