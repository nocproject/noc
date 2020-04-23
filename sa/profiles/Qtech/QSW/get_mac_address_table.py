# ---------------------------------------------------------------------
# Qtech.QSW.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Qtech.QSW.get_mac_address_table"
    interface = IGetMACAddressTable

    always_prefer = "C"

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)", re.MULTILINE
    )
    rx_line1 = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\S+\s+(?P<interfaces>\S+)",
        re.MULTILINE,
    )

    def execute_snmp(self, interface=None, vlan=None, mac=None, **kwargs):
        # SNMP not working!!!
        raise NotImplementedError

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        r = []

        # Fallback to CLI
        cmd = "show mac"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        if interface is not None and mac is None:
            interface = interface[1:]
            cmd += " interface ethernet %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan

        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            cmd = cmd.replace("mac", "mac-address-table")
            try:
                v = self.cli(cmd)
            except self.CLISyntaxError:
                # Not supported at all
                raise self.NotSupportedError()
        for match in self.rx_line.finditer(v):
            interfaces = match.group("interfaces")
            if interfaces == "0" or interfaces.lower() == "cpu":
                continue
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": {"dynamic": "D", "static": "S", "permanent": "S", "self": "S"}[
                        match.group("type").lower()
                    ],
                }
            )
        for match in self.rx_line1.finditer(v):
            interfaces = match.group("interfaces")
            if interfaces == "0" or interfaces.lower() == "cpu":
                continue
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": {
                        "dynamic": "D",
                        "static": "S",
                        "secured": "S",
                        "permanent": "S",
                        "self": "S",
                    }[match.group("type").lower()],
                }
            )
        return r
