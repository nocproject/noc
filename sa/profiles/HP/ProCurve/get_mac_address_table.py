# ---------------------------------------------------------------------
# HP.ProCurve.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC Modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "HP.ProCurve.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_fdb_vlan = re.compile(r"dot1qVlanFdbId\.\d+\.(\d+)\s*=\s*(\d+)")
    rx_line = re.compile(r"dot1qTpFdbPort\.(\d+)\.(\S+)\s*=\s*(\d+)")
    rx_if = re.compile(r"ifName\.(\d+)\s*=\s*(\S+)")

    def execute_cli(self, **kwargs):
        if self.is_old_cli:
            raise NotImplementedError("Old CLI with SNMP only access")
        r = []
        v = self.cli("display mac-address")
        for row in v.split("\n\n")[0].splitlines()[1:]:
            if not row.strip():
                continue
            mac, vlan_id, state, port, _ = row.split(maxsplit=4)
            if mac == "000000-000008":
                continue
            port = self.profile.convert_interface_name(port)
            r += [{"vlan_id": vlan_id, "mac": mac, "interfaces": [port], "type": "D"}]
        return r
