# ----------------------------------------------------------------------
# ResourceGroup Group loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.resourcegroup import ResourceGroup
from noc.inv.models.resourcegroup import ResourceGroup as ResourceGroupModel
from noc.inv.models.technology import Technology


class ResourceGroupLoader(BaseLoader):
    """
    Resource group loader
    """

    name = "resourcegroup"
    model = ResourceGroupModel
    data_model = ResourceGroup

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["technology"] = Technology.get_by_name
