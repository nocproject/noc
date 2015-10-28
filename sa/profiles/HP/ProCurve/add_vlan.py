# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IAddVlan


class Script(BaseScript):
    name = "HP.ProCurve.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d" % vlan_id)
            self.cli("name %s" % name)
            if tagged_ports:
                self.cli("tagged " + " " . join(tagged_ports))
            self.cli("exit")
        self.save_config()
        return True
