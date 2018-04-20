# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.dbtrigger application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models.dbtrigger import DBTrigger


class DBTriggerApplication(ExtModelApplication):
    """
    DBTrigger application
    """
    title = "DB Triggers"
    menu = "Setup | DB Triggers"
    model = DBTrigger
    icon = "icon_database_gear"
