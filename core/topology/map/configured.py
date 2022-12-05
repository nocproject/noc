# ----------------------------------------------------------------------
# Configured Map class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import itertools
from typing import Dict, List, Optional, Iterable, Any, Literal
from dataclasses import dataclass

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.topology.base import (
    TopologyBase,
    MapItem,
    PathItem,
    MapSize,
    BackgroundImage,
)
from noc.inv.models.configuredmap import ConfiguredMap
from noc.inv.models.configuredmap import NodeItem as NodeConfigItem
from noc.inv.models.link import Link
from noc.inv.models.interface import Interface
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.managedobject import ManagedObject


@dataclass
class NodeItem(object):
    id: str
    type: Literal["objectgroup", "managedobject", "objectsegment", "other"] = "other"
    node_id: Optional[str] = None
    level: int = 25
    # Title
    name: str = ""
    title_position: str = ""
    # Size
    width: Optional[int] = None
    height: Optional[int] = None
    attrs: Dict[str, Any] = None


class ConfiguredTopology(TopologyBase):

    name = "configured"
    header = "Configured Map"
    NORMALIZE_POSITION = False

    def __init__(self, gen_id, node_hints=None, link_hints=None, force_spring=False):
        self.cfgmap: ConfiguredMap = ConfiguredMap.get_by_id(gen_id)
        super().__init__(
            gen_id, node_hints=node_hints, link_hints=link_hints, force_spring=force_spring
        )

    def get_size(self) -> Optional[MapSize]:
        return MapSize(height=self.cfgmap.height, width=self.cfgmap.width)

    @classmethod
    def iter_maps(
        cls,
        parent: str = None,
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

    @property
    def background(self) -> Optional[str]:
        return str(self.cfgmap.background_image.id) if self.cfgmap.background_image else None

    def get_background(self) -> Optional[BackgroundImage]:
        if self.cfgmap.background_image:
            return BackgroundImage(
                image=str(self.cfgmap.background_image.id), opacity=self.cfgmap.background_opacity
            )
        return

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
                attrs = {"role": "segment", "address": mo.address, "level": mo.object_profile.level}
                self.add_node(mo, "managedobject", attrs)
        # Process all links
        for link in links:
            if not self.cfgmap.add_linked_node and set(link.linked_objects) - object_ids:
                continue
            self.add_link(link)

    def get_node(self, config: NodeConfigItem) -> NodeItem:
        ni = NodeItem(
            id=config.id,
            type=config.node_type,
            node_id=config.object.id if config.object else None,
            level=25,
            name=config.name,
        )
        if config.node_type == "managedobject":
            ni.attrs = {
                "role": "segment",
                "node_id": config.object.id,
                "address": config.object.address,
                "level": config.object.object_profile.level,
            }
        elif config.node_type in {"objectgroup", "objectsegment"}:
            ni.attrs = {
                "role": "segment",
                "node_id": str(config.object.id),
                "level": self.DEFAULT_LEVEL,
            }
        if self.cfgmap.enable_node_portal and config.portal:
            ni.attrs["portal"] = config.portal

        return ni

    def load(self):
        parent_links = []
        object_mos = set()
        nodes: Dict[str, Any] = {}
        # Extract Nodes
        for nc in self.cfgmap.nodes:
            ni = self.get_node(nc)
            if nc.node_type == "managedobject":
                object_mos.add(nc.object.id)
            if nc.parent:
                parent_links.append((nc.node_id, nc.parent))
                ni.level -= 5
            nodes[ni.node_id] = ni.id
            self.add_node(ni, ni.type, ni.attrs)
            if not nc.add_nested:
                continue
            if nc.node_type == "objectgroup" and nc.object:
                object_mos = object_mos.union(
                    set(ResourceGroup.get_model_instance_ids("sa.ManagedObject", str(nc.object.id)))
                )
            elif nc.node_type == "objectsegment" and nc.object:
                object_mos = object_mos.union(
                    set(nc.object.managed_objects.values_list("id", flat=True))
                )
        for mo in ManagedObject.objects.filter(id__in=list(object_mos)).iterator():
            self.add_node(
                mo,
                "managedobject",
                {
                    "role": "segment",
                    "node_id": mo.id,
                    "address": mo.address,
                    "level": mo.object_profile.level,
                },
            )
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
