# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linux.RHEL.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces, InterfaceTypeError
#from noc.sa.profiles.Cisco.IOS import uBR

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
            r"\d+: (?P<name>\S+):\s[a-zA-Z0-9,<>_ ]+\n"
            r"    link/ether (?P<mac>\S+) brd"
            , re.I | re.S 
        )

        interfaces = []
        # Ethernet ports
        ifcfg = ""
        ifcfg = self.cli("ip link", cached=True)

        for match in re.finditer(rx_iface, ifcfg):
            interfaces += [{
                "name": match.group("name"),
                "type": "physical",
                "mac": match.group("mac"),
                "subinterfaces": []
            }]
        return [{"interfaces": interfaces}]


