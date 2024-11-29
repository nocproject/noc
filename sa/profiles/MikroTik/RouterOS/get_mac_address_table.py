# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_mac_address_table"
    interface = IGetMACAddressTable
    always_prefer = "S"

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "/interface ethernet switch host print detail without-paging where dynamic"
        out = []
        if mac is not None:
            cmd += " mac-address=%s" % mac
        if interface is not None:
            cmd += " ports=%s" % interface
        if vlan is not None:
            cmd += " vlan-id=%d" % vlan
        try:
            v = self.cli_detail(cmd)
        except self.CLISyntaxError:
            return []
        for n, f, r in v:
            if "vlan-id" not in r:
                break
            if r["vlan-id"] == "0":
                continue
            out.append(
                {
                    "vlan_id": r["vlan-id"],
                    "mac": r["mac-address"],
                    "interfaces": [r["ports"]],
                    "type": "D",
                }
            )

        return out
