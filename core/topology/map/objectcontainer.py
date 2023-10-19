# ----------------------------------------------------------------------
# PoP Access Map class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
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
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem

logger = logging.getLogger(__name__)


class ObjectContainerTopology(TopologyBase):
    name = "objectcontainer"
    header = "Object Container Map"
    POP_MODEL = "PoP | Access"
    POP_REGIONAL_MODEL = "PoP | Regional"
    PARAMS = {"container"}
    CONTAINER_MODELS = None

    def __init__(self, container, **settings):
        self.container = Object.get_by_id(container)
        self.logger = PrefixLoggerAdapter(logger, self.container.name)
        super().__init__(**settings)

    def gen_id(self) -> Optional[str]:
        return str(self.container.id)

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        if parent == cls.name:
            parent = None
        if not cls.CONTAINER_MODELS:
            cls.CONTAINER_MODELS = list(
                ObjectModel.objects.filter(
                    data__match={"interface": "container", "attr": "container", "value": True},
                ).values_list("id")
            )
        data = Object.objects.filter(container=parent, model__in=cls.CONTAINER_MODELS).order_by(
            "name"
        )
        print(parent, cls.CONTAINER_MODELS, data)
        if query:
            data = data.filter(name__icontains=query)
        # Apply paging
        if limit:
            data = data[start : start + limit]
        for cont in data:
            yield MapItem(
                title=str(cont.name),
                generator=cls.name,
                id=str(cont.id),
                has_children=cont.has_children,
            )

    @classmethod
    def iter_path(cls, gen_id) -> Iterable[PathItem]:
        o = Object.get_by_id(gen_id)
        if not o:
            return
        for level, ns_id in enumerate(o.get_path(), start=1):
            cont = Object.get_by_id(ns_id)
            yield PathItem(title=str(cont.name), id=str(cont.id), level=level)

    def load(self):
        """
        Load all managed objects from Object Group
        """
        # Group objects
        object_mos: List[int] = list(
            ManagedObject.objects.filter(container__in=self.container.get_nested_ids()).values_list(
                "id", flat=True
            )
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
        for mo in mos.values():
            n = mo.get_topology_node()
            self.add_node(n, {"role": "segment"})
        # Process all links
        for link in links:
            self.add_link(link)
