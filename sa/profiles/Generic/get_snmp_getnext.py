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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSNMPGetNext


class Script(NOCScript):
    name = "Generic.get_snmp_getnext"
    implements = [IGetSNMPGetNext]
    requires = []

    def execute(self, oid, community_suffix=None, bulk=True,
                min_index=None, max_index=None):
        try:
            return list(self.snmp.getnext(oid=oid,
                                 community_suffix=community_suffix,
                                 min_index=min_index, max_index=max_index))
        except self.snmp.TimeOutError:
            return None
