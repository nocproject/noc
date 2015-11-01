# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.isyncvlans import ISyncVlans


class Script(BaseScript):
    name = "Generic.sync_vlans"
    interface = ISyncVlans
    requires = ["get_vlans", "add_vlan", "remove_vlan"]

    def execute(self, vlans, tagged_ports):
        v_map = {}
        for v in vlans:
            v_map[v["vlan_id"]] = v["name"]
        r_vlans = self.scripts.get_vlans()
        dev_vlans = set([v["vlan_id"] for v in r_vlans])
        db_vlans = set([v["vlan_id"] for v in vlans])
        # Do not provision VLAN1
        if 1 in dev_vlans:
            dev_vlans.remove(1)
        if 1 in db_vlans:
            db_vlans.remove(1)
        #
        to_create = db_vlans - dev_vlans
        for vlan in to_create:
            self.scripts.add_vlan(vlan_id=vlan, name=v_map[vlan],
                tagged_ports=tagged_ports)
        to_remove = dev_vlans - db_vlans
        for vlan in to_remove:
            self.scripts.remove_vlan(vlan_id=vlan)

        return {
            "created": list(to_create),
            "removed": list(to_remove)
        }
