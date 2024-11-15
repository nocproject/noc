# ----------------------------------------------------------------------
# Configured Map class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
from typing import Dict, List, Optional, Iterable, Any

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.topology.base import TopologyBase
from noc.core.topology.types import MapItem, PathItem, BackgroundImage, MapMeta, Layout
from noc.inv.models.configuredmap import ConfiguredMap
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.cpe import CPE
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ConfiguredTopology(TopologyBase):
    name = "configured"
    header = _("Configured Map")

    NORMALIZE_POSITION = False
    ISOLATED_WIDTH = 600

    def __init__(self, gen_id, **settings):
        self.cfgmap: ConfiguredMap = ConfiguredMap.get_by_id(gen_id)
        super().__init__(**settings)

    @property
    def gen_id(self) -> Optional[str]:
        return str(self.cfgmap.id)

    @property
    def meta(self) -> MapMeta:
        return MapMeta(
            title=self.title,
            image=(
                BackgroundImage(
                    image=str(self.cfgmap.background_image.id),
                    opacity=self.cfgmap.background_opacity,
                )
                if self.cfgmap.background_image
                else None
            ),
            width=self.cfgmap.width,
            height=self.cfgmap.height,
            layout=Layout(self.cfgmap.layout),
        )

    @classmethod
    def is_empty(cls) -> bool:
        return not bool(ConfiguredMap._get_collection().find_one({}, {"_id": 1}))

    @classmethod
    def iter_maps(
        cls,
        parent: str | None = None,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        start: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Iterable[MapItem]:
        data = ConfiguredMap.objects.filter().order_by("name")
        if query:
            data = data.filter(name__icontains=query)
        # Apply paging
        if limit:
            data = data[start : start + limit]
        for cfg in data:
            yield MapItem(
                title=str(cfg.name),
                generator=cls.name,
                id=str(cfg.id),
                has_children=False,
            )

    @classmethod
    def iter_path(cls, gen_id) -> Iterable[PathItem]:
        cfg = ConfiguredMap.get_by_id(gen_id)
        yield PathItem(title=str(cfg.name), id=str(cfg.id), level=1)

    def add_objects_links(self, object_ids: List[int]):
        """
        Add ManagedObject Links to topology
        :param object_ids:
        :return:
        """
        # Get all links, belonging to object list
        links: List[Link] = list(Link.objects.filter(linked_objects__in=object_ids))
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
        object_ids = set(object_ids)
        # Bulk fetch all managed objects
        if self.cfgmap.add_linked_node:
            external_mos = list(
                set(
                    i["managed_object"]
                    for i in self._interface_cache.values()
                    if "managed_object" in i
                )
                - object_ids
            )
            for mo in ManagedObject.objects.filter(id__in=external_mos):
                self.add_node(mo.get_topology_node(), {"role": "segment"})
        # Process all links
        for link in links:
            if not self.cfgmap.add_linked_node and set(link.linked_objects) - object_ids:
                continue
            self.add_link(link)

    def load(self):
        parent_links = []
        object_mos = set()
        object_cpes = set()
        nodes: Dict[str, Any] = {}
        # Extract Nodes
        for nc in self.cfgmap.nodes:
            ni = nc.get_topology_node()
            if ni.parent:
                parent_links.append((nc.id, ni.parent))
                ni.level -= 5
            if self.cfgmap.enable_node_portal and nc.portal:
                ni.portal = nc.portal
            nodes[nc.node_id] = ni.id
            self.add_node(ni)
            if not nc.add_nested:
                continue
            print("Nested", nc.node_type, nc.object)
            if nc.node_type == "objectgroup" and nc.object:
                object_mos = object_mos.union(
                    set(ResourceGroup.get_model_instance_ids("sa.ManagedObject", str(nc.object.id)))
                )
            elif nc.node_type == "objectsegment" and nc.object:
                object_mos = object_mos.union(
                    set(nc.object.managed_objects.values_list("id", flat=True))
                )
            elif nc.node_type == "container" and nc.object:
                object_mos = object_mos.union(
                    set(
                        ManagedObject.objects.filter(container=nc.object).values_list(
                            "id", flat=True
                        )
                    )
                )
                object_cpes = object_cpes.union(
                    {
                        a.value
                        for a in itertools.chain.from_iterable(
                            Object.objects.filter(
                                data__match={
                                    "interface": "cpe",
                                    "attr": "cpe_id",
                                    "value__exists": True,
                                },
                                container=nc.object,
                            ).values_list("data")
                        )
                        if a.attr == "cpe_id"
                    }
                )
            elif nc.node_type == "managedobject" and nc.object:
                object_cpes = object_cpes.union(
                    {
                        str(cpe)
                        for cpe in CPE.objects.filter(controller=nc.object).values_list("_id")
                    }
                )

        for mo in ManagedObject.objects.filter(id__in=list(object_mos)).iterator():
            self.add_node(mo.get_topology_node(), {"role": "segment"})
        for cpe in CPE.objects.filter(id__in=list(object_cpes)):
            self.add_node(cpe.get_topology_node())
        # Add parent links
        for child_id, parent_id in parent_links:
            self.add_parent(parent_id, child_id)
        if self.cfgmap.add_topology_links:
            self.add_objects_links(list(object_mos))
        # Add Relation
        for ll in self.cfgmap.links:
            if ll.source_node not in nodes or ll.target_nodes[0] not in nodes:
                continue
            self.add_parent(nodes[ll.source_node], nodes[ll.target_nodes[0]])

    @staticmethod
    def q_node(node):
        """
        Format graph node
        :param node:
        :return:
        """
        x = node.copy()
        if "mo" in x:
            del x["mo"]
            x["external"] = x.get("role") != "segment"
        elif node["type"] == "cloud":
            del x["link"]
            x["external"] = False
        return x
