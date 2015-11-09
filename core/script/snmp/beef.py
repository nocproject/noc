# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Beefed SNMP
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import SNMP


class BeefSNMP(SNMP):
    def __init__(self, script):
        super(BeefSNMP, self).__init__(script)
        self.beef = self.beef = self.script.credentials["beef"]

    def get(self, oids, cached=False):
        try:
            self.logger.info("OIDS: %s", oids)
            self.logger.info("%r", self.beef.snmp_get[oids])
            return self.beef.snmp_get[oids]
        except KeyError:
            raise SNMP.TimeOutError()

    def set(self, *args):
        raise NotImplementedError()

    def count(self, oid, filter=None):
        raise NotImplementedError()

    def getnext(self, oid, community_suffix=None,
                filter=None, cached=False,
                only_first=False, bulk=None):
        try:
            return self.beef.snmp_getnext[oid]
        except KeyError:
            raise SNMP.TimeOutError()
