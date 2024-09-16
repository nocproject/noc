# ---------------------------------------------------------------------
# Alstec.24xx.get_mac_address_table
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
    name = "Alstec.24xx.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_all_v = re.compile(
        r"^(?P<vlan_id>\S\S:\S\S):(?P<mac>\S+)\s+(?P<interface>\S+)\s+\d+\s+" r"(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_all = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<vlan_id>\d+)\s+" r"(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_iface = re.compile(r"^\s*(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s*\n", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-addr-table"
        rx_line = self.rx_all
        if interface is not None:
            """
            #show mac-addr-table interface 0/0
            ERROR: interface 0/0 not exist
            """
            if interface == "0/0":
                return []
            cmd += " interface %s" % interface
            rx_line = self.rx_iface
        r = []
        v = self.cli(cmd)
        if "IfIndex" in v:
            # Old format table
            rx_line = self.rx_all_v
        for match in rx_line.finditer(v):
            if match.group("type") == "Learned":
                mtype = "D"
            elif match.group("type") == "Management":
                mtype = "C"
            else:
                mtype = "S"
            if interface is not None:
                _iface = interface
            else:
                _iface = match.group("interface")
            if vlan is not None:
                _vlan = vlan
            elif len(match.group("vlan_id")) == 5:
                _vlan = int((match.group("vlan_id")).replace(":", ""), 16)
            else:
                _vlan = int(match.group("vlan_id"))

            r.append(
                {"vlan_id": _vlan, "mac": match.group("mac"), "interfaces": [_iface], "type": mtype}
            )
        return r
