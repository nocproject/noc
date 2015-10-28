# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IAddVlan


class Script(BaseScript):
    name = "Alcatel.AOS.add_vlan"
    interface = IAddVlan

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d enable name %s" % (vlan_id, name))
            if tagged_ports:
                for port in tagged_ports:
                    self.cli("vlan %d 802.1q 1/%s" % (vlan_id, port))
        self.save_config()
        return True
