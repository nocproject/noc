# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.database application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.db import PMDatabase


class PMDatabaseApplication(ExtDocApplication):
    """
    PMDatabase application
    """
    title = "PM Database"
    menu = "Setup | PM Databases"
    model = PMDatabase
