# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.RTBSv1.get_chassis_id"
    cache = True
    interface = IGetChassisID
    always_prefer = "S"

    rx_iface = re.compile(r"^\s*WAN:\s+(?P<ifname>br\d+)", re.MULTILINE)
    rx_mac = re.compile(r"^\s*br\d+ mac:\s+(?P<mac>\S+)", re.MULTILINE)

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}

    def execute_cli(self):
        try:
            c = self.cli("show interface list")
        except self.CLISyntaxError:
            raise NotImplementedError("Not support getting information by CLI")
        match = self.rx_iface.search(c)
        ifname = match.group("ifname")
        c = self.cli("show interface %s mac" % ifname)
        match = self.rx_mac.search(c)
        return [{"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}]
