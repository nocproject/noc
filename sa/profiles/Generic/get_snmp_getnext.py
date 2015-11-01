# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.get_snmp_getnext
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetsnmpget import IGetSNMPGetNext


class Script(BaseScript):
    name = "Generic.get_snmp_getnext"
    interface = IGetSNMPGetNext
    requires = []

    def execute(self, oid, community_suffix=None, bulk=True,
                min_index=None, max_index=None):
        try:
            return list(self.snmp.getnext(
                oid=oid,
                community_suffix=community_suffix
            ))
        except self.snmp.TimeOutError:
            return None
