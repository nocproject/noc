# ----------------------------------------------------------------------
# SegmentTopology class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import logging
import itertools
from collections import defaultdict
from typing import Dict, List, Set, Optional, Iterable

# Third-party modules
import cachetools
from bson import ObjectId

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.ip import IP
from noc.core.graph.nexthop import iter_next_hops
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem, Portal, MapMeta
from noc.core.translation import ugettext as _

logger = logging.getLogger(__name__)


class SegmentTopology(TopologyBase):
    name = "segment"
    header = _("Network Segment Schemas")
    CAPS: Set[str] = {"Network | STP"}
    PARAMS = {"segment"}

    def __init__(self, segment, **settings):
        self.segment = (
            segment if isinstance(segment, NetworkSegment) else NetworkSegment.get_by_id(segment)
        )
        self.logger = PrefixLoggerAdapter(logger, self.segment.name)
        self.segment_siblings = self.segment.get_siblings()
        self._uplinks_cache = {}
        self.segment_objects = set()
        if self.segment.parent:
            self.parent_segment = self.segment.parent
            self.ancestor_segments = set(self.segment.get_path()[:-1])
        else:
            self.parent_segment = None
            self.ancestor_segments = set()
        super().__init__(**settings)

    @property
    def gen_id(self) -> Optional[str]:
        return str(self.segment.id)

    @property
    def title(self):
        return self.segment.name

    @property
    def meta(self) -> MapMeta:
        return MapMeta(
            title=self.title,
            max_links=self.segment.max_shown_downlinks,
        )

    def get_role(self, mo: ManagedObject) -> str:
        if mo.segment in self.segment_siblings:
            return "segment"
        elif self.parent_segment and mo.segment.id in self.ancestor_segments:
            return "uplink"
        else:
            return "downlink"

    @cachetools.cachedmethod(operator.attrgetter("_uplinks_cache"))
    def get_uplinks(self) -> List[str]:
        self.logger.info("Searching for uplinks")
        if not self.G:
            return []
        for policy in self.segment.profile.iter_uplink_policy():
            uplinks = getattr(self, f"get_uplinks_{policy}")()
            if uplinks:
                self.logger.info(
                    "[%s] %d uplinks found: %s",
                    policy,
                    len(uplinks),
                    ", ".join(str(x) for x in uplinks),
                )
                return uplinks
            self.logger.info("[%s] No uplinks found. Skipping", policy)
        self.logger.info("Failed to find uplinks")
        return []

    def get_uplinks_seghier(self) -> List[str]:
        """
        Find uplinks basing on segment hierarchy. Any object with parent segment
        is uplink
        :return:
        """
        return [i for i in self.G.nodes if self.G.nodes[i].get("role") == "uplink"]

    def get_uplinks_molevel(self) -> List[str]:
        """
        Find uplinks basing on Managed Object's level. Top-leveled objects are returned.
        :return:
        """
        max_level = max(
            self.G.nodes[i].get("level")
            for i in self.G.nodes
            if self.G.nodes[i].get("type") == "managedobject"
        )
        return [
            i
            for i in self.G.nodes
            if self.G.nodes[i].get("type") == "managedobject"
            and self.G.nodes[i].get("level") == max_level
        ]

    def get_uplinks_seg(self) -> List[str]:
        """
        All segment objects are uplinks
        :return:
        """
        return [i for i in self.G.nodes if self.G.nodes[i].get("role") == "segment"]

    def get_uplinks_minaddr(self) -> List[str]:
        """
        Segment's Object with lesser address is uplink
        :return:
        """
        s = next(
            iter(
                sorted(
                    (IP.prefix(self.G.nodes[i].get("address")), i)
                    for i in self.G.nodes
                    if self.G.nodes[i].get("role") == "segment"
                )
            )
        )
        return [s[1]]

    def get_uplinks_maxaddr(self) -> List[str]:
        """
        Segment's Object with greater address is uplink
        :return:
        """
        s = next(
            reversed(
                sorted(
                    (IP.prefix(self.G.nodes[i].get("address")), i)
                    for i in self.G.nodes
                    if self.G.nodes[i].get("role") == "segment"
                )
            )
        )
        return [s[1]]

    def load(self):
        """
        Load all managed objects from segment
        """
        # Get all links, belonging to segment
        links: List[Link] = list(
            Link.objects.filter(linked_segments__in=[s.id for s in self.segment_siblings])
        )
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
        segment_mos: Set[int] = set(self.segment.managed_objects.values_list("id", flat=True))
        all_mos: List[int] = list(
            set(
                i["managed_object"] for i in self._interface_cache.values() if "managed_object" in i
            )
            | segment_mos
        )
        mos: Dict[int, "ManagedObject"] = {
            mo.id: mo for mo in ManagedObject.objects.filter(id__in=all_mos)
        }
        self.segment_objects: Set[int] = set(
            mo_id for mo_id in all_mos if mos[mo_id].segment.id == self.segment.id
        )
        for mo in mos.values():
            if mo.state.is_wiping:
                continue
            n = mo.get_topology_node()
            role = self.get_role(mo)
            if role == "uplink":
                n.portal = Portal(generator="segment", id=str(self.parent_segment.id))
            elif role == "downlink":
                n.portal = Portal(generator="segment", id=str(mo.segment.id))
            self.add_node(n, {"role": role})
            # self.add_object(mo)
        # Process all segment's links
        for link in links:
            self.add_link(link)

    def iter_uplinks(self):
        """
        Yields ObjectUplinks items for segment

        :returns: ObjectUplinks items
        """

        def get_node_uplinks(node: str) -> List[str]:
            role = self.G.nodes[node].get("role", "cloud")
            if role == "uplink":
                # Only downlinks matter
                return []
            elif role == "downlink":
                # All segment neighbors are uplinks.
                # As no inter-downlink segment's links are loaded
                # so all neigbors are from current segment
                return list(self.G.neighbors(node))
            # Segment role and clouds
            ups = {}
            for u in uplinks:
                if u == node:
                    # skip self
                    continue
                for next_hop, path_len in iter_next_hops(self.G, node, u):
                    ups[next_hop] = min(path_len, ups.get(next_hop, path_len))
            # Shortest path first
            return sorted(ups, key=lambda x: ups[x])

        from noc.sa.models.managedobject import ObjectUplinks

        uplinks = self.get_uplinks()
        # @todo: Workaround for empty uplinks
        # Get uplinks for cloud nodes
        cloud_uplinks: Dict[str, List[int]] = {
            o: [int(u) for u in get_node_uplinks(o)]
            for o in self.G.nodes
            if self.G.nodes[o]["type"] == "cloud"
        }
        # All objects including neighbors
        all_objects: Set[str] = set(
            o for o in self.G.nodes if self.G.nodes[o]["type"] == "managedobject"
        )
        # Get objects uplinks
        obj_uplinks: Dict[int, List[int]] = {}
        obj_downlinks: Dict[int, Set[int]] = defaultdict(set)
        for o in all_objects:
            mo = int(o)
            ups: List[int] = []
            for u in get_node_uplinks(o):
                cu = cloud_uplinks.get(u)
                if cu is not None:
                    # Uplink is a cloud. Use cloud's uplinks instead
                    ups += cu
                else:
                    ups += [int(u)]
            obj_uplinks[mo] = ups
            for u in ups:
                obj_downlinks[u].add(mo)
        # Check uplinks with DownlinkMerge settings
        dlm_settings: Set[int] = set(
            ManagedObject.objects.filter(
                id__in=obj_uplinks, object_profile__enable_rca_downlink_merge=True
            ).values_list("id", flat=True)
        )
        # Calculate RCA neighbors and yield result
        for mo in obj_uplinks:
            # Filter out only current segment. Neighbors will be updated by their
            # segment's tasks
            if mo not in self.segment_objects:
                continue
            # All uplinks
            neighbors = set(obj_uplinks[mo])
            # All downlinks
            for dmo in obj_downlinks[mo]:
                neighbors.add(dmo)
                # And uplinks of downlinks
                neighbors |= set(obj_uplinks[dmo])
            # Downlinks of uplink if MergeDownlinks setting is set
            if dlm_settings and dlm_settings.intersection(set(obj_uplinks[mo])):
                for dumo in obj_uplinks[mo]:
                    neighbors |= obj_downlinks[dumo]
            # Not including object itself
            if mo in neighbors:
                neighbors.remove(mo)
            #
            rca_neighbors = list(sorted(neighbors))
            # Recalculated result
            yield ObjectUplinks(
                object_id=mo,
                uplinks=obj_uplinks[mo],
                rca_neighbors=rca_neighbors,
            )

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        if parent is not None:
            data = NetworkSegment.objects.filter(parent=parent).order_by("name")
        else:
            data = NetworkSegment.objects.filter().order_by("name")
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
        o = NetworkSegment.get_by_id(gen_id)
        if not o:
            return
        for level, ns_id in enumerate(o.get_path(), start=1):
            ns = NetworkSegment.get_by_id(ns_id)
            yield PathItem(title=str(ns.name), id=str(ns.id), level=level)
