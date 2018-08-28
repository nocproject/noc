# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ResourceGroup Group loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from base import BaseLoader
from noc.inv.models.resourcegroup import ResourceGroup


class ResourceGroupLoader(BaseLoader):
    """
    Administrative division loader
    """
    name = "resourcegroup"
    model = ResourceGroup
    fields = [
        "id",
        "name",
        "technology",
        "parent"
        "description"
    ]

    mapped_fields = {
        "parent": "resourcegroup"
    }
