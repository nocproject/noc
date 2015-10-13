# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OMap API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.service.api.base import API, api, lock
from noc.main.models.pool import Pool
from noc.sa.models.objectmap import ObjectMap


class OMapAPI(API):
    """
    Monitoring API
    """
    name = "omap"

    @api
    @lock("lock-omap-%(env)s")
    def get_syslog_mappings(self, pool):
        """
        Returns a dict of ip -> object id for syslog sources
        """
        p = Pool.objects.filter(name=pool).first()
        if not p:
            return {}
        return ObjectMap.get_syslog_sources(p)

    @api
    @lock("lock-omap-%(env)s")
    def get_trap_mappings(self, pool):
        """
        Returns a dict of ip -> object id for trap sources
        """
        p = Pool.objects.filter(name=pool).first()
        if not p:
            return {}
        return ObjectMap.get_syslog_sources(p)

    @api
    @lock("lock-omap-%(env)s")
    def get_ping_mappings(self, pool):
        """
        Returns a dict of ip -> {"id": ..., "status": ..., "interval": ...}
        """
        p = Pool.objects.filter(name=pool).first()
        if not p:
            return {}
        return ObjectMap.get_ping_sources(p)
