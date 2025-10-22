# ---------------------------------------------------------------------
# Iskratel.MSAN.get_mac_address_table
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
    name = "Iskratel.MSAN.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_line2 = re.compile(r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s*\n", re.MULTILINE)
    rx_line3 = re.compile(
        r"^\s*(?P<vlan_id>[0-9A-F]{2}:[0-9A-F]{2}):"
        r"(?P<mac>[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})\s+"
        r"(?P<interface>\d+/\d+)\s+\d+\s+(?P<type>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_line4 = re.compile(
        r"^(?P<mac>\S+)\s+(?P<interface>\d+/\d+)\s+(?P<type>\S+)\s*\n", re.MULTILINE
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-addr-table"
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if mac is not None:
            cmd += " %s" % mac
        macs = self.cli(cmd)
        r = []
        for match in self.rx_line.finditer(macs):
            if match.group("type") == "Learned":
                mtype = "D"
            else:
                mtype = "S"
            r.append(
                {
                    "vlan_id": int(match.group("vlan_id")),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": mtype,
                }
            )
        if (not r) and (interface is not None):
            for match in self.rx_line2.finditer(macs):
                if match.group("type") == "Learned":
                    mtype = "D"
                else:
                    mtype = "S"
                r.append(
                    {
                        "vlan_id": int(match.group("vlan_id")),
                        "mac": match.group("mac"),
                        "interfaces": [interface],
                        "type": mtype,
                    }
                )
        if not r:
            for match in self.rx_line3.finditer(macs):
                if match.group("type") == "Learned":
                    mtype = "D"
                elif match.group("type") == "Management":
                    mtype = "C"
                else:
                    mtype = "S"
                r.append(
                    {
                        "vlan_id": int(match.group("vlan_id").replace(":", ""), 16),
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interface")],
                        "type": mtype,
                    }
                )

        if not r:
            if vlan is None:
                vlans = self.scripts.get_vlans()
            else:
                vlans = [{"vlan_id": vlan}]
            for v in vlans:
                macs = self.cli("show mac-addr-table vlan %s" % v["vlan_id"])
                for match in self.rx_line4.finditer(macs):
                    if match.group("type") == "Learned":
                        mtype = "D"
                    else:
                        mtype = "S"
                    r.append(
                        {
                            "vlan_id": int(v["vlan_id"]),
                            "mac": match.group("mac"),
                            "interfaces": [match.group("interface")],
                            "type": mtype,
                        }
                    )
        return r
