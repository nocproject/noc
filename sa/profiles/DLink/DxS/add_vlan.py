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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "DLink.DxS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("create vlan %s tag %d" % (name, vlan_id))
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("config vlan %s add tagged %s" % (name, port))
        self.save_config()
        return True
