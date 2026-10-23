# ---------------------------------------------------------------------
# Arista.EOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Arista.EOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>DYNAMIC|STATIC)\s+(?P<interfaces>\S+)"
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if mac is not None:
            cmd += f" address {self.profile.convert_mac(mac)}"
        if interface is not None:
            # @todo: Fix
            cmd += f" interface {interface}"
        if vlan is not None:
            cmd += f" vlan {vlan}"
        r = []
        macs = self.cli(cmd)
        for line in macs.splitlines():
            line = line.strip()
            if line.startswith("Multicast"):
                break
            match = self.rx_line.match(line)
            if match:
                mac = match.group("mac")
                interfaces = [i.strip() for i in match.group("interfaces").split(",")]
                if not interfaces:
                    continue
                m_type = {"dynamic": "D", "static": "S"}.get(match.group("type").lower())
                if not m_type:
                    continue
                r.append(
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": mac,
                        "interfaces": interfaces,
                        "type": m_type,
                    }
                )
        return r
