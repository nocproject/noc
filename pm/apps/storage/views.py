# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.storage application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.storage import PMStorage


class PMStorageApplication(ExtDocApplication):
    """
    PMStorage application
    """
    title = "Storage"
    menu = "Setup | PM Storages"
    model = PMStorage
