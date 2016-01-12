# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Administrative Domain loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.sa.models.administrativedomain import AdministrativeDomain


class AdminitstrativeDomainLoader(BaseLoader):
    """
    Administrative Domain loader
    """
    name = "administrativedomain"
    model = AdministrativeDomain
    fields = [
        "id",
        "name",
    ]
