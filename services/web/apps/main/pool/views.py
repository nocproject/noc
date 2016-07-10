# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pool application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.main.models.pool import Pool


class PoolApplication(ExtDocApplication):
    """
    Pool application
    """
    title = "Pool"
    menu = "Setup | Pools"
    model = Pool
    glyph = "database"
