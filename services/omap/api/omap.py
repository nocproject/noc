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
from noc.lib.service.api.base import ServiceAPI, api
from noc.main.models.pool import Pool
from noc.sa.models.objectmap import ObjectMap


class OMapAPI(ServiceAPI):
    """
    Monitoring API
    """
    name = "omap"
    level = ServiceAPI.AL_GLOBAL

    @api
    def get_syslog_mappings(self, pool):
        """
        Returns a dict of ip -> object id for syslog sources
        """
        p = Pool.objects.filter(name=pool).first()
        if not p:
            return {}
        return ObjectMap.get_syslog_sources(p)

    @api
    def get_trap_mappings(self, pool):
        """
        Returns a dict of ip -> object id for trap sources
        """
        p = Pool.objects.filter(name=pool).first()
        if not p:
            return {}
        return ObjectMap.get_syslog_sources(p)
