# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.CER.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iremovevlan import IRemoveVlan


class Script(BaseScript):
    """
    Brocade.CER.remove_vlan
    """
    name = 'Brocade.CER.remove_vlan'
    interface = IRemoveVlan

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.configure():
            self.cli('no vlan %d' % vlan_id)
        return True
