# ---------------------------------------------------------------------
# HP.Comware.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "HP.Comware.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>\S{4}-\S{4}-\S{4})\s+(?P<vlan_id>\d+)\s+(?P<if_type>\S+)"
        r"\s+(?P<interface>\S+)\s+\S+",
        re.IGNORECASE | re.DOTALL | re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "display mac-address"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        for ll in macs.splitlines():
            match = self.rx_line.match(ll.strip())
            if not match:
                continue
            if match.group("if_type") == "Learned":
                if_type = "D"
            else:
                if_type = "S"
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": if_type,
                }
            ]
        return r
