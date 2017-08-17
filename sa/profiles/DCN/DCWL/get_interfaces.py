# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4

class Script(BaseScript):
    name = "DCN.DCWL.get_interfaces"
    cache = True
    interface = IGetInterfaces

    INTERFACE_TYPES = {

            "lo": "loopback",  # Loopback

        }

    INTERFACE_TYPES2 = {

            "brv": "unknown",  # No comment
            "eth": "physical",  # No comment
            "wla": "physical",  # No comment

        }

    @classmethod
    def get_interface_type(cls, name):
         c = cls.INTERFACE_TYPES2.get(name[:3])
         if c:
            return c
         c = cls.INTERFACE_TYPES.get(name[:2])
         return c

    def execute(self):
        interfaces = []
        r = []
        c = self.cli("get interface all", cached=True)
        for line in c.splitlines():
            r = line.split(' ', 1)
            if r[0] == "name":
                name = r[1].strip()
                iftype = self.get_interface_type(name)
                if not name:
                    self.logger.info(
                        "Ignoring unknown interface type: '%s", iftype
                    )
                    continue
            if r[0] == "mac":
                mac = r[1].strip()
            if r[0] == "ip":
                ip_address = r[1].strip()
            if r[0] == "mask":
                ip_subnet = r[1].strip()
                #ip address + ip subnet
                if ip_subnet or ip_address:
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    interfaces += [{
                        "type": iftype,
                        "name": name,
                        "mac": mac,
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "enabled_afi": ["IPv4"],
                            "ipv4_addresses": [ip_address],
                        }]
                    }]
                #no ip address + ip subnet
                else:
                    interfaces += [{
                        "type": iftype,
                        "name": name,
                        "mac": mac,
                        "subinterfaces": [{
                            "name": name,
                            "mac": mac,
                            "enabled_afi": ["BRIDGE"],
                        }]
                    }]
        return [{"interfaces": interfaces}]
