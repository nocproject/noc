# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_vlans
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "Huawei.VRP3.get_vlans"
    interface = IGetVlans
    rx_vlan1 = re.compile(r"^\s+(?P<vlanid>\d+)\s+\d+\s+\d+\s+\S+",
        re.MULTILINE | re.DOTALL)
    rx_vlan2 = re.compile(r"^\s+\d+\s+(?P<vlanid>\d+)\s+\d+\s+\d+",
        re.MULTILINE | re.DOTALL)
    rx_vlan3 = re.compile(r"^\s+Inband VLAN is\s+(?P<vlanid>\d+)")

    def execute(self):
        r = []
        try:
            c = self.cli("show vlan all")
            for match in self.rx_vlan1.finditer(c):
                if int(match.group('vlanid')) == 1:
                    continue
                r += [{"vlan_id": int(match.group('vlanid'))}]
        except self.CLISyntaxError:
            c = self.cli("show vlan 0")
            for match in self.rx_vlan2.finditer(c):
                if int(match.group('vlanid')) == 1:
                    continue
                r += [{"vlan_id": int(match.group('vlanid'))}]
            try:
                with self.configure():
                    c = self.cli("show nms")
                    match = self.rx_vlan3.search(c)
                    if match:
                        r += [{"vlan_id": int(match.group('vlanid'))}]
            except:
                pass
        return r
