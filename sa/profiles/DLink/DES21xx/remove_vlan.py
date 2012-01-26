# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IRemoveVlan


class Script(NOCScript):
    name = "DLink.DES21xx.remove_vlan"
    implements = [IRemoveVlan]

    def execute(self, vlan_id):
        self.cli("delete vlan tag %d" % vlan_id)
        self.save_config()
        return True
