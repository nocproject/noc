# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.MSAN.get_vlans"
    interface = IGetVlans

    rx_vlan1 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+\S+(\s+[XF]+)?\s*(?P<name>.*)$", re.MULTILINE)
    rx_vlan2 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<name>.+)\s*$", re.MULTILINE)

    def execute(self):
        r = []
        try:
            for match in self.rx_vlan1.finditer(self.cli("vlan show")):
                vid = int(match.group("vlan_id"))
                if vid == 1:
                    continue
                name = match.group("name")
                if name != "":
                    r += [{"vlan_id": vid, "name": name}]
                else:
                    r += [{"vlan_id": vid}]
        except self.CLISyntaxError:
            try:
                for match in self.rx_vlan2.finditer(self.cli("switch vlan show *")):
                    vid = int(match.group("vlan_id"))
                    if vid == 1:
                        continue
                    name = match.group("name")
                    if name != "-":
                        r += [{"vlan_id": vid, "name": name}]
                    else:
                        r += [{"vlan_id": vid}]
            except self.CLISyntaxError:
                # XXX try to use "vlan1q vlan status"
                pass
        return r
