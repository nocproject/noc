# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.storage application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.storage import Storage


class StorageApplication(ExtDocApplication):
    """
    Storage application
    """
    title = "Storage"
    menu = "Setup | Storages"
    model = Storage
    query_fields = ["name", "description"]
