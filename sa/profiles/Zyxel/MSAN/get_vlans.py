# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.MSAN.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Zyxel.MSAN.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan1 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+\S+(\s+[XF]+)?\s*(?P<name>.*)$", re.MULTILINE
    )
    rx_vlan2 = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<name>.+)\s*$", re.MULTILINE)
    rx_vlan3 = re.compile(r"^\s*(?P<vlan_id>\d+)\s+V\s*$", re.MULTILINE)

    def execute(self):
        r = []
        try:
            v = self.cli("vlan show", cached=True)
            for match in self.rx_vlan1.finditer(v):
                vid = int(match.group("vlan_id"))
                if vid == 1:
                    continue
                name = match.group("name")
                if name != "":
                    r += [{"vlan_id": vid, "name": name}]
                else:
                    r += [{"vlan_id": vid}]
            return r
        except self.CLISyntaxError:
            pass
        try:
            v = self.cli("switch vlan show *")
        except self.CLISyntaxError:
            try:
                v = self.cli("vlan1q vlan status")
            except self.CLISyntaxError:
                v = ""
        if v:
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
        try:
            v = self.cli("lcman svlan show", cached=True)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_vlan3.finditer(v):
            vid = int(match.group("vlan_id"))
            if vid == 1:
                continue
            r += [{"vlan_id": vid}]
        return r
