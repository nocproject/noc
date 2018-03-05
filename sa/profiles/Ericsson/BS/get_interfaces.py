# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.BS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ericsson.BS.get_interfaces"
    interface = IGetInterfaces

    rx_int = re.compile("(?P<ifname>NCAETH:\d+)[\S\s]+hwaddress:(?P<mac>\S+)[\S\s]+mtu:(?P<mtu>\S+)?", re.MULTILINE)

    def execute(self):
        interfaces = []
        v = self.cli("devinfo")
        match = self.rx_int.search(v.split("\n\n")[0])
        ifname = match.group("ifname")
        mac = match.group("mac")
        mtu = match.group("mtu")
        interfaces += [{
            "type": "physical",
            "name": ifname,
            "mac": mac,
            "admin_status": True,
            "oper_status": True,
            "subinterfaces": [{
                "name": ifname,
                "mac": mac,
                "mtu": mtu,
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ["BRIDGE"]
            }]
        }]
        return [{"interfaces": interfaces}]
