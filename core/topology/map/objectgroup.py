# ----------------------------------------------------------------------
# ObjectGroupTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import itertools
from typing import Dict, List, Optional, Iterable

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.topology.base import TopologyBase, MapItem, PathItem

logger = logging.getLogger(__name__)


class ObjectGroupTopology(TopologyBase):
    name = "objectgroup"
    header = "Object Group Schemas"

    def __init__(self, gen_id, node_hints=None, link_hints=None, force_spring=False):
        self.rg = ResourceGroup.get_by_id(gen_id)
        self.logger = PrefixLoggerAdapter(logger, self.rg.name)
        super().__init__(
            gen_id, node_hints=node_hints, link_hints=link_hints, force_spring=force_spring
        )

    def load(self):
        """
        Load all managed objects from Object Group
        """
        # Group objects
        object_mos: List[int] = ResourceGroup.get_model_instance_ids(
            "sa.ManagedObject", str(self.rg.id)
        )
        # Get all links, belonging to segment
        links: List[Link] = list(Link.objects.filter(linked_objects__in=object_mos))
        # All linked interfaces from map
        all_ifaces: List["ObjectId"] = list(
            itertools.chain.from_iterable(link.interface_ids for link in links)
        )
        # Bulk fetch all interfaces data
        self._interface_cache: Dict["ObjectId", "Interface"] = {
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
        all_mos: List[int] = list(
            set(
                i["managed_object"] for i in self._interface_cache.values() if "managed_object" in i
            )
            | set(object_mos)
        )
        mos: Dict[int, "ManagedObject"] = {
            mo.id: mo for mo in ManagedObject.objects.filter(id__in=all_mos)
        }
        # self.group_objects: Set[int] = set(
        #     mo_id for mo_id in all_mos if mos[mo_id].segment.id == self.segment.id
        # )
        for mo in mos.values():
            attrs = {"role": "segment", "address": mo.address, "level": mo.object_profile.level}
            # if attrs["role"] == "uplink":
            #     attrs["portal"] = {"generator": "segment", "id": self.parent_segment}
            # elif attrs["role"] == "downlink":
            #     attrs["portal"] = {"generator": "segment", "id": str(mo.segment.id)}
            self.add_node(mo, "managedobject", attrs)
            # self.add_object(mo)
        # Process all segment's links
        for link in links:
            self.add_link(link)

    @staticmethod
    def q_mo(d):
        x = d.copy()
        if x["type"] == "managedobject":
            del x["mo"]
            x["external"] = x.get("role") != "segment"
        elif d["type"] == "cloud":
            del x["link"]
            x["external"] = False
        return x

    def iter_nodes(self):
        for n in self.G.nodes.values():
            yield self.q_mo(n)

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        data = ResourceGroup.objects.filter(parent=parent).order_by("name")
        if query:
            data = data.filter(name__icontains=query)
        # Apply paging
        if limit:
            data = data[start : start + limit]
        for ns in data:
            yield MapItem(
                title=str(ns.name),
                generator=cls.name,
                id=str(ns.id),
                has_children=ns.has_children,
            )

    @classmethod
    def iter_path(cls, gen_id) -> Iterable[PathItem]:
        o = ResourceGroup.get_by_id(gen_id)
        if not o:
            return
        for level, ns_id in enumerate(o.get_path(), start=1):
            ns = ResourceGroup.get_by_id(ns_id)
            yield PathItem(title=str(ns.name), id=str(ns.id), level=level)
