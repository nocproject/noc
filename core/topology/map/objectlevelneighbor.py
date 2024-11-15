# ----------------------------------------------------------------------
# ObjectGroupTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import itertools
from typing import Iterable

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem, Portal
from noc.core.translation import ugettext as _

logger = logging.getLogger(__name__)


class ObjectLevelNeighborTopology(TopologyBase):
    name = "objectlevelneighbor"
    header = _("Object Level Neighbor Schemas")

    PARAMS = {"mo_id"}

    def __init__(self, mo_id, **settings):
        self.mo = ManagedObject.get_by_id(mo_id)
        self.logger = PrefixLoggerAdapter(logger, self.mo.name)
        super().__init__(**settings)

    def gen_id(self) -> str | None:
        return str(self.mo.id)

    def load(self):
        """
        Load all managed objects from Object Group
        """
        # Group objects
        object_mos: list[int] = self.mo.links[:]
        if not object_mos:
            # Only current node
            self.add_node(self.mo.get_topology_node(), {"role": "segment"})
            return
        level = self.mo.object_profile.level
        while object_mos:
            for links, n_level in ManagedObject.objects.filter(id__in=object_mos).values_list(
                "links", "object_profile__level"
            ):
                object_mos += links
                if n_level > level:
                    level = n_level
            if level > self.mo.object_profile.level:
                break

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
            set(
                i["managed_object"] for i in self._interface_cache.values() if "managed_object" in i
            )
            | set(object_mos)
        )
        mos: dict[int, ManagedObject] = {
            mo.id: mo for mo in ManagedObject.objects.filter(id__in=all_mos)
        }
        o_mos = set(object_mos)
        for mo in mos.values():
            if mo.state.is_wiping:
                continue
            n = mo.get_topology_node()
            if mo.id not in o_mos:
                n.portal = Portal(generator=self.name, id=str(mo.id))
            self.add_node(n, {"role": "segment"})
        # Process all links
        for link in links:
            self.add_link(link)

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: str | None = None,
        limit: int | None = None,
        start: int | None = None,
        page: int | None = None,
    ) -> Iterable[MapItem]:
        data = ManagedObject.objects.filter().order_by("name")
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
                has_children=False,
            )

    @classmethod
    def iter_path(cls, gen_id) -> Iterable[PathItem]:
        o = ManagedObject.get_by_id(gen_id)
        if not o:
            return
        yield PathItem(title=str(o.name), id=str(o.id), level=1)
