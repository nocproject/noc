# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IRemoveVlan


class Script(NOCScript):
    """
    Brocade.IronWare.remove_vlan
    """
    name = "Brocade.IronWare.remove_vlan"
    implements = [IRemoveVlan]

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli("no vlan %d" % vlan_id)
        return True
