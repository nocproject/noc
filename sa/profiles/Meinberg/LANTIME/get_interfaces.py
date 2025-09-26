# ---------------------------------------------------------------------
# Meinberg.LANTIME.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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


class Script(BaseScript):
    name = "Meinberg.LANTIME.get_interfaces"
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

    def execute_cli(self, **kwargs):
        interfaces = []
        # Ethernet ports
        ifcfg = self.cli("ip link", cached=True)

        for match in self.rx_iface.finditer(ifcfg):
            # bonding interface: bondX
            if "MASTER" in match.group("status"):
                typeif = "aggregated"

                interfaces += [
                    {
                        "type": typeif,
                        "mac": match.group("mac"),
                        "subinterfaces": [{"name": match.group("name"), "enabled_afi": ["BRIDGE"]}],
                    }
                ]

                # Bridge: brX, vnetX, virbrX, vifX.X, vethX(XEN), xenbr0, tapX, xapiX, ovs-system
                if match.group("name")[:4] in [
                    "vnet",
                    "virb",
                    "veth",
                    "xenb",
                    "xapi",
                    "ovs-",
                ] or match.group("name")[:2] in ["br", "vi", "ta"]:
                    interfaces += [
                        {
                            "name": match.group("name"),
                            "type": typeif,
                            "mac": match.group("mac"),
                            "subinterfaces": [],
                        }
                    ]

            # only:  eth0-N, enpXsX, emX,
            if match.group("name")[:2] in ["et", "en", "em", "pe"]:
                typeif = "physical"
                # 2: eth0: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master bond0 state UP qlen 1000
                # slave interface in bonding
                if "SLAVE" in match.group("status"):
                    ifmaster = self.cli("ip link show " + match.group("name"), cached=True)
                    for slaveif in self.rx_master.finditer(ifmaster):
                        # print slaveif.group("master"), "ddddddddddddddddddd"
                        interfaces += [
                            {
                                "name": match.group("name"),
                                "type": typeif,
                                "mac": match.group("mac"),
                                "subinterfaces": [],
                                "aggregated_interface": slaveif.group("master"),
                            }
                        ]
                else:
                    interfaces += [
                        {
                            "name": match.group("name"),
                            "type": typeif,
                            "mac": match.group("mac"),
                            "subinterfaces": [],
                        }
                    ]

        return [{"interfaces": interfaces}]
