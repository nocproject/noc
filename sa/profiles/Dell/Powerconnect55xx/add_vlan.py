# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Dell.Powerconnect55xx.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.add_vlan"
    interface = IAddVlan
=======
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    name = "Dell.Powerconnect55xx.add_vlan"
    implements = [IAddVlan]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan database")
            self.cli("vlan %d" % vlan_id)
            self.cli("exit")
            self.cli("interface vlan %d" % vlan_id)
            self.cli("name \"%s\"" % name)
        self.save_config()
        return True
