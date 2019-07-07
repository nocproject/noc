# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        try:
            v = self.cli_detail(
                "/interface ethernet switch vlan print detail without-paging", cached=True
            )
            r = [{"vlan_id": d["vlan-id"]} for n, f, d in v if not f]
        except self.CLISyntaxError:
            r = []
        try:
            v = self.cli_detail("/interface bridge vlan print detail without-paging", cached=True)
            for n, f, d in v:
                if "X" in f or "D" in f:
                    continue
                vlans = self.expand_rangelist(d["vlan-ids"])
                for vlan in vlans:
                    for i in r:
                        if i["vlan_id"] == vlan:
                            break
                    else:
                        r += [{"vlan_id": vlan}]
        except self.CLISyntaxError:
            pass
        return r
