# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Cisco.IOS.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^(?:\*\s+)?(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+"
        r"(?:\S+\s+){0,2}(?P<interfaces>.*)$"
    )
    rx_line2 = re.compile(
        r"^(?P<mac>\S+)\s+(?P<type>\S+)\s+(?P<vlan_id>\d+)\s+" r"(?P<interfaces>.*)$"
    )  # Catalyst 3500XL
    ignored_interfaces = (
        "router",
        "switch",
        "stby-switch",
        "yes",
        "no",
        "-",
        "cpu",
        "drop",
        "<drop>",
    )

    def is_ignored_interface(self, i):
        if i.lower() in self.ignored_interfaces:
            return True
        if i.startswith("flood to vlan"):
            return True
        if i.startswith("VPLS"):
            return True
        if i.startswith("seq_no:"):
            return True
        if is_int(i):
            # 10.27.0.80, 1204773146
            return True
        return False

    def execute_cli(self, interface=None, vlan=None, mac=None):
        def qn(s):
            s = s.strip()
            if s.startswith("Eth VLAN "):
                return s[4:]
            else:
                return s

        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            cmd = cmd.replace("mac address-table", "mac-address-table")
            try:
                macs = self.cli(cmd)
            except self.CLISyntaxError:
                # Not supported at all
                raise self.NotSupportedError()
        r = []
        for line in macs.splitlines():
            if line.startswith("Multicast Entries"):
                break  # Additional section on 4500
            line = line.strip()
            match = self.rx_line.match(line)
            if not match:
                match = self.rx_line2.match(line)  # 3500XL variant
            if match:
                mac = match.group("mac")
                if mac.startswith("3333."):
                    continue  # Static entries
                interfaces = [qn(i) for i in match.group("interfaces").split(",")]
                interfaces = [i for i in interfaces if not self.is_ignored_interface(i)]
                if not interfaces:
                    continue
                m_type = {"dynamic": "D", "static": "S"}.get(match.group("type").lower())
                if not m_type:
                    continue
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": mac,
                        "interfaces": interfaces,
                        "type": m_type,
                    }
                ]
        return r
