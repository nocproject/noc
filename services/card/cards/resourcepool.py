# ----------------------------------------------------------------------
# ResourcePool card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import datetime
import operator
from typing import List, Optional

# Python modules
from pydantic import BaseModel

# NOC modules
from noc.inv.models.resourcepool import ResourcePool
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from .base import BaseCard


class ResourceKey(BaseModel):
    key: str
    domain: Optional[str] = None


class AllocatorRequest(BaseModel):
    # [{"domain": XXX, "key": XXXX}]
    keys: List[ResourceKey]
    resource_pool: str
    limit: int = 1
    tt_id: Optional[str] = None
    allocated_till: Optional[datetime.date] = None
    action: str = "allocate"
    confirm: bool = False


class ResourcePoolCard(BaseCard):
    name = "resourcepool"
    default_template_name = "resourcepool"
    model = ResourcePool
    actions = ["allocate"]

    def get_data(self):
        # Build upwards path
        #
        prefixes = sorted(
            Prefix.get_by_resource_pool(self.object),
            key=operator.attrgetter("prefix"),
        )
        return {
            "object": self.object,
            "domains": prefixes,
            "resources": list(Address.objects.filter(prefix__in=prefixes).order_by("address")),
        }

    @classmethod
    def allocate(
        cls,
        item: AllocatorRequest,
    ):
        """
        keys: [{"domain": XXX, "key": XXXX}]
        resource_pool: str
        limit: int = 1
        action: free | reserve = reserve
        confirm: bool
        """
        print("Allocator", item)
        # keys
        # resource_pool
        #
        return cls.render()
