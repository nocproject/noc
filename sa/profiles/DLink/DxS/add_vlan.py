# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.add_vlan
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
    name = "DLink.DxS.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("create vlan %s tag %d" % (name, vlan_id))
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("config vlan %s add tagged %s" % (name, port))
        self.save_config()
        return True
