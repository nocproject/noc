# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_vlans"
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
                v = self.cli("switch vlan show *")
            except self.CLISyntaxError:
                v = self.cli("vlan1q vlan status")
            for match in self.rx_vlan2.finditer(v):
                vid = int(match.group("vlan_id"))
                if vid == 1:
                    continue
                name = match.group("name")
                if not name.startswith("-"):
                    r += [{"vlan_id": vid, "name": name}]
                else:
                    r += [{"vlan_id": vid}]
        return r
