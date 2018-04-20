# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.get_snmp_getnext
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetsnmpget import IGetSNMPGetNext


class Script(BaseScript):
    name = "Generic.get_snmp_getnext"
    interface = IGetSNMPGetNext
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    requires = []

    def execute(self, oid, community_suffix=None, bulk=True,
                min_index=None, max_index=None):
        try:
<<<<<<< HEAD
            return list(self.snmp.getnext(
                oid=oid,
                community_suffix=community_suffix
            ))
=======
            return list(self.snmp.getnext(oid=oid,
                                 community_suffix=community_suffix,
                                 min_index=min_index, max_index=max_index))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        except self.snmp.TimeOutError:
            return None
