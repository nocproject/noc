# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_snmp_get
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSNMPGet


class Script(NOCScript):
    name = "Generic.get_snmp_get"
    implements = [IGetSNMPGet]
    requires = []

    def execute(self, oid, community_suffix=None):
        try:
            return self.snmp.get(oid, community_suffix)
        except self.snmp.TimeOutError:
            return None
