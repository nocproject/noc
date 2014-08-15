# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        r = []
        if self.snmp and self.access_profile.snmp_ro:
            try:
                pmib = self.profile.get_pmib(self.scripts.get_version())
                if pmib is None:
                    raise NotImplementedError()
                for oid, v in self.snmp.getnext(pmib + ".7.6.1.1",
                                                bulk=True):  # dot1qVlanFdbId
                    r += [{"vlan_id": oid.split(".")[-1], "name": v}]
            except self.snmp.TimeOutError:
                pass
            return r
        else:
            raise self.NotSupportedError()
