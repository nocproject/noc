# ----------------------------------------------------------------------
# ResourceGroup Group loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.resourcegroup import ResourceGroup as ResourceGroupModel
from noc.inv.models.technology import Technology

from ..models.resourcegroup import ResourceGroup
from .base import BaseLoader


class ResourceGroupLoader(BaseLoader):
    """
    Resource group loader
    """

    name = "resourcegroup"
    model = ResourceGroupModel
    data_model = ResourceGroup

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.clean_map["technology"] = Technology.get_by_name
