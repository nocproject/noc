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
from fastapi import status
from fastapi.responses import RedirectResponse

# NOC modules
from noc.inv.models.resourcepool import ResourcePool
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from noc.wf.models.state import State
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
        domain = self.handler.get_argument("domain", strict=False)
        limit = self.handler.get_argument("limit", strict=False)
        free_only = self.handler.get_argument("free_only", strict=False)
        if domain:
            resources = Address.objects.filter(prefix=domain)
        else:
            resources = Address.objects.filter(prefix__in=prefixes)
        if free_only:
            states = list(State.objects.filter(name="Free"))
            resources = resources.filter(state__in=states)
        return {
            "object": self.object,
            "domains": prefixes,
            "resources": list(resources.order_by("address")),
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
        for a in Address.objects.filter(address__in=[x.key for x in item.keys]):
            if item.action == "allocate":
                a.reserve(
                    allocated_till=item.allocated_till,
                    reservation_id=item.tt_id,
                    confirm=item.confirm,
                )
            elif item.action == "free":
                new_state = a.profile.workflow.get_default_state()
                a.set_state(new_state)
        return RedirectResponse(
            f"/api/card/view/{cls.name}/{item.resource_pool}/",
            status_code=status.HTTP_200_OK,
        )
