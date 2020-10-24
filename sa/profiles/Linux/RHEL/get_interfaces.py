# ---------------------------------------------------------------------
# Linux.RHEL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Important see: https://ru.wikipedia.org/w/index.php?oldid=75745192

"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces

"""
need Iproute2

see http://linux-net.osdl.org/index.php/Iproute2

# yum -y install iproute

or

# dnf -y install iproute

"""


class Script(BaseScript):
    name = "Linux.RHEL.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ \-]+\n"
        r"    link\/ether (?P<mac>\S+) brd",
        re.IGNORECASE | re.DOTALL,
    )

    rx_master = re.compile(
        r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ ]+ master (?P<master>\S+)\s.*\n"
        r"    link\/ether (?P<mac>\S+) brd",
        re.IGNORECASE | re.DOTALL,
    )
    PHY_NAMES2 = {"br", "vi", "ta"}
    PHY_NAMES_SL2 = {"et", "en", "em", "pe"}
    PHY_NAMES4 = {"vnet", "virb", "veth", "xenb", "xapi", "ovs-"}

    def execute(self, interface=None):
        interfaces = []
        # Ethernet ports
        ifcfg = self.cli("ip link", cached=True)
        for match in self.rx_iface.finditer(ifcfg):
            if_name = match.group("name")
            # bonding interface: bondX
            if "MASTER" in match.group("status"):
                typeif = "aggregated"
                interfaces += [
                    {
                        "name": if_name,
                        "type": typeif,
                        "mac": match.group("mac"),
                        "subinterfaces": [{"name": if_name, "enabled_afi": ["BRIDGE"]}],
                    }
                ]

            # Bridge: brX, vnetX, virbrX, vifX.X, vethX(XEN), xenbr0, tapX, xapiX, ovs-system
            if if_name[:4] in self.PHY_NAMES4 or if_name[:2] in self.PHY_NAMES2:
                typeif = "physical"
                interfaces += [
                    {
                        "name": if_name,
                        "type": typeif,
                        "mac": match.group("mac"),
                        "subinterfaces": [],
                    }
                ]
            # only:  eth0-N, enpXsX, emX,
            if if_name[:2] in self.PHY_NAMES_SL2:
                typeif = "physical"
                # 2: eth0: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master bond0 state UP qlen 1000
                # slave interface in bonding
                if "SLAVE" in match.group("status"):
                    ifmaster = self.cli("ip link show %s" % if_name, cached=True)
                    for slaveif in self.rx_master.finditer(ifmaster):
                        # print slaveif.group("master"), "ddddddddddddddddddd"
                        interfaces += [
                            {
                                "name": if_name,
                                "type": typeif,
                                "mac": match.group("mac"),
                                "subinterfaces": [],
                                "aggregated_interface": slaveif.group("master"),
                            }
                        ]
                else:
                    interfaces += [
                        {
                            "name": if_name,
                            "type": typeif,
                            "mac": match.group("mac"),
                            "subinterfaces": [],
                        }
                    ]
        return [{"interfaces": interfaces}]
