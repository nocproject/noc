# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_mac_address_table"
    interface = IGetMACAddressTable
    MAX_REPETITIONS = 40
    MAX_GETNEXT_RETIRES = 1
    BULK = None

    mac_status_map = {
        1: "S",  # Other
        2: "S",  # Invalid
        3: "D",  # Learned
        4: "C",  # Self
        5: "C",  # MGMT
    }

    def execute_snmp(self, interface=None, vlan=None, mac=None):
        r = []
        iface_map = {
            i["ifindex"]: i["interface"]
            for i in self.scripts.get_interface_properties(enable_ifindex=True)
        }
        port_oid = mib["Q-BRIDGE-MIB::dot1qTpFdbPort"]
        status_oid = mib["Q-BRIDGE-MIB::dot1qTpFdbStatus"]
        if vlan:
            port_oid = mib["Q-BRIDGE-MIB::dot1qTpFdbPort", vlan]
            status_oid = mib["Q-BRIDGE-MIB::dot1qTpFdbStatus", vlan]
        mac_port = {}
        for r_oid, iface in self.snmp.getnext(
            port_oid,
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            bulk=self.get_bulk(),
        ):
            if not iface:
                # For iface == 0
                continue
            r_oid = r_oid.rsplit(".", 7)[-7:]
            if iface not in iface_map:
                self.logger.error(
                    "Unknown interface index %s, for MAC: %s",
                    iface,
                    ":".join("%02x" % int(c) for c in r_oid[1:]),
                )
                continue
            iface = iface_map[iface]
            if interface and iface != interface:
                continue
            mac_port[tuple(r_oid)] = iface
        # Apply status
        for r_oid, status in self.snmp.getnext(
            status_oid,
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            bulk=self.get_bulk(),
        ):
            r_oid = tuple(r_oid.rsplit(".", 7)[-7:])
            if r_oid not in mac_port:
                continue
            vlan_id, mac = r_oid[0], ":".join("%02x" % int(c) for c in r_oid[1:])
            r += [
                {
                    "interfaces": [mac_port[r_oid]],
                    "mac": mac,
                    "type": self.mac_status_map[status],
                    "vlan_id": max(int(vlan_id), 1),
                }
            ]
        return r

    def get_max_repetitions(self):
        return self.MAX_REPETITIONS

    def get_getnext_retires(self):
        return self.MAX_GETNEXT_RETIRES

    def get_bulk(self):
        return self.BULK
