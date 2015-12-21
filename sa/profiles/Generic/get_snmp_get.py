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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetsnmpget import IGetSNMPGet


class Script(BaseScript):
    name = "Generic.get_snmp_get"
    interface = IGetSNMPGet
    requires = []

    def execute(self, oid):
        try:
            return self.snmp.get(oid)
        except self.snmp.TimeOutError:
            return None
