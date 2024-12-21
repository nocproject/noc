# ---------------------------------------------------------------------
# Generic.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.mib import mib
from noc.core.validators import is_vlan


class Script(BaseScript):
    name = "Generic.get_mac_address_table"
    interface = IGetMACAddressTable
    MAX_REPETITIONS = 20
    MAX_GETNEXT_RETIRES = 1

    BULK = None

    mac_status_map = {
        1: "S",  # Other
        2: "S",  # Invalid
        3: "D",  # Learned
        4: "C",  # Self
        5: "C",  # MGMT
    }

    def get_iface_mapping(self):
        # Get PID -> ifindex mapping
        pid_iface_map = {}
        r = {}
        for oid, v in self.snmp.getnext(
            mib["BRIDGE-MIB::dot1dBasePortIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            bulk=self.get_bulk(),
        ):
            pid_iface_map[int(oid.split(".")[-1])] = v
        for i in self.scripts.get_interface_properties(enable_ifindex=True):
            if i["ifindex"] not in pid_iface_map:
                self.logger.warning("[%s] Not PID iface mapping: %s", i["interface"], r)
                continue
            r[i["ifindex"]] = i["interface"]
        return r

    def execute_snmp(self, interface=None, vlan=None, mac=None):
        r = []
        iface_map = self.get_iface_mapping()
        self.logger.debug("Interface map: %s", iface_map)
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
            r_oid = tuple(r_oid.rsplit(".", 7)[-7:])
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
            mac_port[r_oid] = iface
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
            # Some devices return CPU/management vlan as 0
            if vlan_id != "0" and not is_vlan(vlan_id):
                # Found vlan `4155` on Eltex MES-3124F fw 2.5.48.6
                self.logger.error(
                    "Invalid vlan number %s, for MAC: %s, Port: %s", vlan_id, mac, mac_port[r_oid]
                )
                continue
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
