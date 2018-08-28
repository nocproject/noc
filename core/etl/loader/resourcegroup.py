# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ResourceGroup Group loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseLoader
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.technology import Technology


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
        "parent",
        "description"
    ]

    mapped_fields = {
        "parent": "resourcegroup"
    }

    def clean(self, row):
        """
        Fix Technology
        """
        v = super(ResourceGroupLoader, self).clean(row)
        v["technology"] = Technology.get_by_name(v["technology"])
        return v
