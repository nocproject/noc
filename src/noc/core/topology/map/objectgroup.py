# ----------------------------------------------------------------------
# ObjectGroupTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import itertools
from collections.abc import Iterable

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem
from noc.core.translation import ugettext as _

logger = logging.getLogger(__name__)


class ObjectGroupTopology(TopologyBase):
    name = "objectgroup"
    header = _("Object Group Schemas")

    PARAMS = {"resource_group"}

    def __init__(self, resource_group, **settings) -> None:
        self.rg = ResourceGroup.get_by_id(resource_group)
        self.logger = PrefixLoggerAdapter(logger, self.rg.name)
        super().__init__(**settings)

    def gen_id(self) -> str | None:
        return str(self.rg.id)

    def load(self):
        """
        Load all managed objects from Object Group
        """
        # Group objects
        object_mos: list[int] = ResourceGroup.get_model_instance_ids(
            "sa.ManagedObject", str(self.rg.id)
        )
        # Get all links, belonging to segment
        links: list[Link] = list(Link.objects.filter(linked_objects__in=object_mos))
        # All linked interfaces from map
        all_ifaces: list["ObjectId"] = list(
            itertools.chain.from_iterable(link.interface_ids for link in links)
        )
        # Bulk fetch all interfaces data
        self._interface_cache: dict["ObjectId", "Interface"] = {
            i["_id"]: i
            for i in Interface._get_collection().find(
                {"_id": {"$in": all_ifaces}},
                {
                    "_id": 1,
                    "managed_object": 1,
                    "name": 1,
                    "bandwidth": 1,
                    "in_speed": 1,
                    "out_speed": 1,
                },
            )
        }
        # Bulk fetch all managed objects
        all_mos: list[int] = list(
            {i["managed_object"] for i in self._interface_cache.values() if "managed_object" in i}
            | set(object_mos)
        )
        mos: dict[int, "ManagedObject"] = {
            mo.id: mo for mo in ManagedObject.objects.filter(id__in=all_mos)
        }
        for mo in mos.values():
            n = mo.get_topology_node()
            self.add_node(n, {"role": "segment"})
        # Process all links
        for link in links:
            self.add_link(link)

    @classmethod
    def is_empty(cls) -> bool:
        return not bool(ResourceGroup._get_collection().find_one({}, {"_id": 1}))

    @classmethod
    def iter_maps(
        cls,
        parent: str | None = None,
        query: str | None = None,
        limit: int | None = None,
        start: int | None = None,
    ) -> Iterable[MapItem]:
        if parent is not None:
            data = ResourceGroup.objects.filter(parent=parent).order_by("name")
        else:
            data = ResourceGroup.objects.filter().order_by("name")
        if query:
            data = data.filter(name__icontains=query)
        # Apply paging
        if limit:
            data = data[start : start + limit]
        for rg in data:
            yield MapItem(
                title=str(rg.name),
                generator=cls.name,
                id=str(rg.id),
                has_children=rg.has_children,
            )

    @classmethod
    def iter_path(cls, gen_id: str) -> Iterable[PathItem]:
        o = ResourceGroup.get_by_id(gen_id)
        if not o:
            return
        for level, ns_id in enumerate(o.get_path(), start=1):
            ns = ResourceGroup.get_by_id(ns_id)
            yield PathItem(title=str(ns.name), id=str(ns.id), level=level)
