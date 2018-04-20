# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Force10.FTOS.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Force10.FTOS.add_vlan"
    interface = IAddVlan
=======
##----------------------------------------------------------------------
## Force10.FTOS.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import noc.sa.script
from noc.sa.interfaces import IAddVlan


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.add_vlan"
    implements = [IAddVlan]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("interface vlan %d" % vlan_id)
            self.cli("name %s" % name)
            for tp in tagged_ports:
                self.cli("tagged %s" % tp)
            self.cli("no shutdown")
            self.cli("exit")
        self.save_config()
        return True
