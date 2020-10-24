# ----------------------------------------------------------------------
# ResourceGroup Group loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.resourcegroup import ResourceGroupModel
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.technology import Technology


class ResourceGroupLoader(BaseLoader):
    """
    Resource group loader
    """

    name = "resourcegroup"
    model = ResourceGroup
    data_model = ResourceGroupModel
    fields = ["id", "name", "technology", "parent", "description"]

    mapped_fields = {"parent": "resourcegroup"}

    def clean(self, row):
        """
        Fix Technology
        """
        v = super().clean(row)
        v["technology"] = Technology.get_by_name(v["technology"])
        return v
