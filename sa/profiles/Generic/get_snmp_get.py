# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.get_snmp_get
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetsnmpget import IGetSNMPGet


class Script(BaseScript):
    name = "Generic.get_snmp_get"
    interface = IGetSNMPGet
    requires = []

    def execute(self, oid):
        try:
            return self.snmp.get(oid)
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        except self.snmp.TimeOutError:
            return None
