# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Administrative Domain loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.sa.models.administrativedomain import AdministrativeDomain

## NOC modules
from base import BaseLoader


class AdminitstrativeDomainLoader(BaseLoader):
    """
    Administrative Domain loader
    """
    name = "administrativedomain"
    model = AdministrativeDomain
    fields = [
        "id",
        "name",
        "parent",
        "default_pool"
    ]
    mapped_fields = {
        "parent": "administrativedomain"
    }
