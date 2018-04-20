# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import logging
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_vlans"
    interface = IGetVlans

    def execute(self):
        r = []
        if self.has_snmp():
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
            try:
                r = []
                vlans = self.profile.get_vlans(self)
                for v in vlans:
                    r += [{
                        "vlan_id": v['vlan_id'],
                        "name": v['vlan_name']
                    }]
                return r
            except:
                raise self.NotSupportedError()
