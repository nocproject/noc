# ---------------------------------------------------------------------
# TPLink.T2600G.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "TPLink.T2600G.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^(?P<mac>[:0-9a-fA-F]+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+"
        r"(?P<type>\w+)\s+\S+",
        re.MULTILINE,
    )

    def get_iface_mapping(self):
        # Get PID -> ifindex mapping
        r = {}
        if not self.is_platform_T2600G:
            return super().get_iface_mapping()
        for i in self.scripts.get_interface_properties(enable_ifindex=True):
            try:
                r[int(i["interface"].split("/")[-1])] = i["interface"]
            except ValueError:
                continue
        return r

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface gi 1/0/%s" % interface.split("/")[2]
        if vlan is not None:
            cmd += " vlan %s" % vlan
        macs = self.cli(cmd)
        r = []
        for match in self.rx_line.finditer(macs):
            m_type = {"dynamic": "D", "static": "S"}.get(match.group("type").lower())
            if not m_type:
                continue
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": m_type,
                }
            ]
        return r
