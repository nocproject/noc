# ----------------------------------------------------------------------
# ResourcePool card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import datetime
from typing import List, Optional

# Python modules
from pydantic import BaseModel
from fastapi import status, Request, Header, HTTPException
from fastapi.responses import RedirectResponse

# NOC modules
from noc.inv.models.resourcepool import ResourcePool
from noc.wf.models.state import State
from .base import BaseCard


class ResourceKey(BaseModel):
    key: Optional[str] = None
    domain: Optional[str] = None


class AllocatorRequest(BaseModel):
    # [{"domain": XXX, "key": XXXX}]
    resource_pool: str
    limit: int = 1
    keys: List[ResourceKey]
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
        domain = self.handler.get_argument("domain", strict=False)
        free_only = self.handler.get_argument("free_only", strict=False)
        domains = []
        for d in self.object.get_resource_domains():
            if domain and str(d.id) != domain:
                continue
            domains.append(d)
        if free_only:
            states = list(State.objects.filter(name="Free"))
        if self.object.type == "ip":
            resources = self.object.resource_model.objects.filter(prefix__in=domains)
            if free_only:
                resources = resources.filter(state__in=states)
        elif self.object.type == "vlan":
            resources = self.object.resource_model.objects.filter(l2_domain__in=domains)
            if free_only:
                resources = resources.filter(state__in=states)
        return {
            "object": self.object,
            "domains": sorted(domains),
            "resources": list(resources.order_by("address")),
        }

    @classmethod
    def allocate(
        cls,
        item: AllocatorRequest,
        request: Request,
        remote_user: Optional[str] = Header(None, alias="Remote-User"),
    ):
        """
        keys: [{"domain": XXX, "key": XXXX}]
        resource_pool: str
        limit: int = 1
        action: free | reserve = reserve
        confirm: bool
        """
        if not remote_user:
            raise HTTPException(404, "Not found")
        pool = ResourcePool.get_by_id(item.resource_pool)
        keys = [k.key for k in item.keys]
        with ResourcePool.acquire([pool]):
            allocator = pool.get_allocator()
            print("Allocate", allocator)
            r = allocator(
                resource_keys=keys or None,
                limit=item.limit,
                reservation_id=item.tt_id,
                allocated_till=item.allocated_till,
                # user=remote_user,
            )
            print("Result", r)
        return RedirectResponse(
            f"/api/card/view/{cls.name}/{item.resource_pool}/",
            status_code=status.HTTP_200_OK,
        )
