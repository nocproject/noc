# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_mac_address_table"
    interface = IGetMACAddressTable
    cached = True

    always_prefer = "S"

    rx_line = re.compile(
        r"(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>Learnt|Static)\s+(?P<interfaces>\S+)",
        re.MULTILINE,
    )
    rx_line1 = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<vlan_name>\S+)?\s+(?P<mac>\S+)\s+"
        r"(?P<interface>\d+)\s+(?P<type>Dynamic|Static)",
        re.MULTILINE,
    )

    T_MAP = {"Learnt": "D", "Dynamic": "D", "Static": "S"}

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        # Fallback to CLI
        r = []
        cmd = "debug info"
        try:
            s = self.cli("debug info")
            for match in self.rx_line.finditer(s):
                m_interface = match.group("interfaces")
                m_vlan = match.group("vlan_id")
                m_mac = match.group("mac")
                if (
                    (interface is None and vlan is None and mac is None)
                    or (interface is not None and interface == m_interface)
                    or (vlan is not None and vlan == m_vlan)
                    or (mac is not None and mac == m_mac)
                ):
                    r += [
                        {
                            "vlan_id": m_vlan,
                            "mac": m_mac,
                            "interfaces": [m_interface],
                            "type": self.T_MAP[match.group("type")],
                        }
                    ]
            return r
        except self.CLISyntaxError:
            pass
        cmd = "show fdb"
        if mac is not None:
            cmd += " mac_address %s" % mac
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            cmd += " vlanid %d" % vlan
        s = self.cli(cmd)
        for match in self.rx_line1.finditer(s):
            m_interface = match.group("interface")
            m_vlan = match.group("vlan_id")
            m_mac = match.group("mac")
            r += [
                {
                    "vlan_id": m_vlan,
                    "mac": m_mac,
                    "interfaces": [m_interface],
                    "type": self.T_MAP[match.group("type")],
                }
            ]
        return r
