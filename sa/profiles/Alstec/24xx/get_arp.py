# ---------------------------------------------------------------------
# Alstec.24xx.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Alstec.24xx.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^vlan \d+\s+(?P<interface>\S+)\s+"
        r"(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+"
        r"(?P<mac>\S+)\s+\S+\s*$",
        re.MULTILINE,
    )

    rx_ip = re.compile(
        r"^\s*IP\sAddress\s*\.+\s(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s*", re.MULTILINE
    )

    rx_mac = re.compile(r"\s*MAC\sAddress\s*\.+\s(?P<MAC_address>\S+)\n", re.MULTILINE)

    rx_ip_gw = re.compile(
        r"^\s*Default\sGateway\s*\.+\s(?P<ip>[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s*", re.MULTILINE
    )

    rx_vlan_gw = re.compile(
        r"^\s*Management\sVLAN\sID\s*\.+\s*(?P<MAC_address>\d+)\s*\n", re.MULTILINE
    )

    def execute(self, interface=None):
        r = []
        v = self.cli("show network")

        ip = self.rx_ip.findall(v)
        mac = self.rx_mac.findall(v)
        gw = self.rx_ip_gw.findall(v)
        gw_vlan = self.rx_vlan_gw.findall(v)

        try:
            macs = parse_table(self.cli("show mac-addr-table vlan 1"))
            try:
                mac_gw = MACAddressParameter().clean(macs[0][0])
            except (ValueError, IndexError):
                macs = parse_table(self.cli("show mac-addr-table vlan %s" % gw_vlan[0]))
                if len(macs[0]) == 3:
                    # Only mac, iface, type
                    mac_gw = MACAddressParameter().clean(
                        next(m[0] for m in macs if m[2] == "Learned")
                    )
                else:
                    mac_gw = MACAddressParameter().clean(
                        next(m[0] for m in macs if m[3] == "Learned")
                    )
        except self.CLISyntaxError:
            macs = parse_table(self.cli("show mac-addr-table"))
            f_mac_gw = [m[0] for m in macs if m[2] == "1"]
            if not f_mac_gw:
                f_mac_gw = [m[0] for m in macs if m[2] == gw_vlan[0] and m[3] == "Learned"]
            mac_gw = f_mac_gw[0]

        if mac_gw:
            r += [{"ip": gw[0], "mac": mac_gw}]

        r += [{"ip": ip[0], "mac": mac[0]}]

        return r
