# ---------------------------------------------------------------------
# Alstec.7200.get_mac_address_table
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
    name = "Alstec.7200.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_all = re.compile(
        r"^(?P<vlan_id>\S\S:\S\S):(?P<mac>\S+)\s+(?P<interface>\S+)\s+\d+\s+" r"(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_iface = re.compile(r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s*\n", re.MULTILINE)
    rx_vlan = re.compile(r"^(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<type>\S+)\s*\n", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-addr-table"
        rx_line = self.rx_all
        if interface is not None:
            cmd += " interface %s" % interface
            rx_line = self.rx_iface
        if vlan is not None:
            cmd += " vlan %s" % vlan
            rx_line = self.rx_vlan
        if (mac is not None) and (vlan is not None):
            cmd += " %s %s" % (mac, vlan)
            rx_line = self.rx_all
        r = []
        for match in rx_line.finditer(self.cli(cmd)):
            if match.group("type") == "Learned":
                mtype = "D"
            elif match.group("type") == "Management":
                mtype = "C"
            else:
                mtype = "S"
            if vlan is not None:
                _vlan = vlan
            elif len(match.group("vlan_id")) == 5:
                _vlan = int((match.group("vlan_id")).replace(":", ""), 16)
            else:
                _vlan = int(match.group("vlan_id"))
            if interface is not None:
                _iface = interface
            else:
                _iface = match.group("interface")
            r.append(
                {"vlan_id": _vlan, "mac": match.group("mac"), "interfaces": [_iface], "type": mtype}
            )
        return r
