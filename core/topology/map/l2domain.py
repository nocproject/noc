# ----------------------------------------------------------------------
# L2DomainTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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
from noc.vc.models.l2domain import L2Domain
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem
from noc.core.translation import ugettext as _

logger = logging.getLogger(__name__)


class L2DomainTopology(TopologyBase):
    name = "l2domain"
    header = _("L2 Domains")

    def __init__(self, l2domain, **settings):
        self.l2domain = L2Domain.get_by_id(l2domain)
        self.logger = PrefixLoggerAdapter(logger, self.l2domain.name)
        super().__init__(**settings)

    def gen_id(self) -> Optional[str]:
        return str(self.l2domain.id)

    def load(self):
        """
        Load all managed objects from Object Group
        """
        # Group objects
        object_mos: List[int] = L2Domain.get_l2_domain_object_ids(str(self.l2domain.id))
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
            {i["managed_object"] for i in self._interface_cache.values() if "managed_object" in i}
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

    @classmethod
    def is_empty(cls) -> bool:
        return not bool(L2Domain._get_collection().find_one({}, {"_id": 1}))

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        data = L2Domain.objects.filter().order_by("name")
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
        o = L2Domain.get_by_id(gen_id)
        if not o:
            return
        yield PathItem(title=str(o.name), id=str(o.id), level=1)
