# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed Object Profile loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.models.managedobjectprofile import ManagedObjectProfile

## NOC modules
from base import BaseLoader


class ManagedObjectProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """
    name = "managedobjectprofile"
    model = ManagedObjectProfile
    fields = [
        "id",
        "name",
        "level"
    ]
