# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP3.add_vlan
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Huawei.VRP3.add_vlan"
    interface = IAddVlan
=======
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "Huawei.VRP3.add_vlan"
    implements = [IAddVlan]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
