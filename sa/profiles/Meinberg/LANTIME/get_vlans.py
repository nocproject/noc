# ---------------------------------------------------------------------
# Meinberg.LANTIME.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Meinberg.LANTIME.get_vlans"
    interface = IGetVlans

    rx_iface = re.compile(
        r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ \-]+\n"
        r"    link\/ether (?P<mac>\S+) brd .*\n"
        r"    vlan protocol 802.1Q id (?P<vlan_number>\d+)\s",
        re.IGNORECASE | re.DOTALL,
    )

    def execute_cli(self, **kwargs):
        """
        $ ip -details link show


        6: bond0.2102@bond0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br1 state UP mode DEFAULT qlen 1000
            link/ether 00:21:5a:5c:d6:b6 brd ff:ff:ff:ff:ff:ff promiscuity 1
            vlan protocol 802.1Q id 2102 <REORDER_HDR>
            bridge_slave addrgenmode eui64
        """

        r = [{"vlan_id": 1}]
        vlans = self.cli("ip -details link show")

        for match in self.rx_iface.finditer(vlans):
            r += [{"vlan_id": match.group("vlan_number")}]

        return r
