# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.remove_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IRemoveVlan


class Script(noc.sa.script.Script):
    name = "Eltex.PON.remove_vlan"
    implements = [IRemoveVlan]

    def execute(self, vlan_id):
        if not self.scripts.has_vlan(vlan_id=vlan_id):
            return False
        with self.profile.switch(self):
#            with self.configure():  # Fix BUG...
                self.cli("configure\r")  # Fix BUG...
                self.cli("no vlan %d\r" % vlan_id)
                self.cli("exit\r")  # Fix BUG...
        self.save_config()
        return True
