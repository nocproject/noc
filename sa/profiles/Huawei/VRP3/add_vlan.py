# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.add_vlan
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IAddVlan


class Script(BaseScript):
    name = "Huawei.VRP3.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("interface lan 0/0 \n")
            self.cli("vlan %d common\n" % (vlan_id))
            self.cli("exit\n")
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("pvc  adsl %s 0 35 lan 0/0 %d 1 disable 1483b off off 1 1" % (port, vlan_id))
        self.save_config()
        return True
