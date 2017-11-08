# -*- coding: utf-8 -*-
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

    def execute(self, interface=None):

        rx_iface = re.compile(
            r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ \-]+\n"
            r"    link\/ether (?P<mac>\S+) brd"
            , re.I | re.S
        )

        rx_master = re.compile(
            r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ ]+ master (?P<master>\S+)\s.*\n"
            r"    link\/ether (?P<mac>\S+) brd"
            , re.I | re.S
        )

        interfaces = []
        # Ethernet ports
        ifcfg = ""
        ifcfg = self.cli("ip link", cached=True)

        for match in re.finditer(rx_iface, ifcfg):
            # print match.group("status")
            # print match.group("name")
            typeif = "other"

            # bonding interface: bondX
            if 'MASTER' in match.group("status"):
                typeif = "aggregated"

                interfaces += [{
                    "name": match.group("name"),
                    "type": typeif,
                    "mac": match.group("mac"),
                    "subinterfaces": [{
                        "name": match.group("name"),
                        "enabled_afi": ["BRIDGE"]
                    }],
                }]

            # Bridge: brX, vnetX, virbrX, vifX.X, vethX(XEN), xenbr0, tapX, xapiX, ovs-system
            if match.group("name")[:4] in ["vnet", "virb", "veth", "xenb", "xapi", "ovs-"] or match.group("name")[
                                                                                              :2] in ["br", "vi", "ta"]:
                typeif = "physical"
                interfaces += [{
                    "name": match.group("name"),
                    "type": typeif,
                    "mac": match.group("mac"),
                    "subinterfaces": []
                }]

            # only:  eth0-N, enpXsX, emX,
            if match.group("name")[:2] in ["et", "en", "em", "pe"]:
                typeif = "physical"
                # 2: eth0: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master bond0 state UP qlen 1000
                # slave interface in bonding
                if 'SLAVE' in match.group("status"):
                    ifmaster = self.cli("ip link show " + match.group("name"), cached=True)
                    for slaveif in re.finditer(rx_master, ifmaster):
                        #                        print slaveif.group("master"), "ddddddddddddddddddd"
                        interfaces += [{
                            "name": match.group("name"),
                            "type": typeif,
                            "mac": match.group("mac"),
                            "subinterfaces": [],
                            "aggregated_interface": slaveif.group("master")
                        }]
                else:
                    interfaces += [{
                        "name": match.group("name"),
                        "type": typeif,
                        "mac": match.group("mac"),
                        "subinterfaces": []
                    }]

        return [{"interfaces": interfaces}]
