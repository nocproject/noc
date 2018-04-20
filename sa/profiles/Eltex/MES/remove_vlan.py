# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Eltex.MES.remove_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import with_statement
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    name = "Eltex.MES.remove_vlan"
    interface = IRemoveVlan
=======
##----------------------------------------------------------------------
## Eltex.MES.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IRemoveVlan


class Script(noc.sa.script.Script):
    name = "Eltex.MES.remove_vlan"
    implements = [IRemoveVlan]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("vlan database")
            self.cli("no vlan %d" % vlan_id)
        self.save_config()
        return True
