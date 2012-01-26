# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "DLink.DES21xx.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        v = self.scripts.get_version()
        cmd = "create vlan tag %d" % vlan_id
        if v["version"][0] >= "5":  # sofrware version 5.0.0 or above
            cmd += " desc %s" % name
        with self.configure():
            self.cli(cmd)
            if tagged_ports:
                for port in tagged_ports:
                    if v["version"][0] >= "5":
                        cmd = "config vlan vid %d add tagged %s" % (vlan_id, port)
                    else:
                        cmd = "config vlan tag %d add tagged %s" % (vlan_id, port)
                    self.cli(cmd)
        self.save_config()
        return True
