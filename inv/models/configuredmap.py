# ---------------------------------------------------------------------
# Configured Map
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Union

# Third-party modules
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    IntField,
    ObjectIdField,
    ReferenceField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.stencil import stencil_registry
from noc.core.topology.types import TopologyNode, Portal
from noc.core.topology.loader import loader as topo_loader
from noc.core.topology.types import Layout
from noc.core.mongo.fields import ForeignKeyField
from noc.main.models.imagestore import ImageStore
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object
from noc.inv.models.link import Link
from noc.inv.models.cpe import CPE


class AlarmFilter(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    alarm_class = ListField(ReferenceField(AlarmClass))
    min_severity = AlarmSeverity
    # drawtype
    # color


class ObjectFilter(EmbeddedDocument):
    segment = ReferenceField(NetworkSegment, required=False)
    resource_group = ReferenceField(ResourceGroup, required=False)
    managed_object = ForeignKeyField(ManagedObject, required=False)
    container = ReferenceField(Object)
    cpe = ReferenceField(CPE)

    def __str__(self):
        return (
            f"Segment: {self.segment}; Group: {self.resource_group}; "
            f"ManagedObject: {self.managed_object}; Container: {self.container}"
        )


class NodeItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    node_id = ObjectIdField(default=bson.ObjectId)
    parent = ObjectIdField()
    # Generator Config
    node_type = StringField(
        choices=["objectgroup", "managedobject", "objectsegment", "cpe", "container", "other"]
    )
    object_filter: ObjectFilter = EmbeddedDocumentField(ObjectFilter)
    add_nested = BooleanField()  # Add nested nodes (if supported) all nodes from group or children
    # Draw block
    shape = StringField(choices=["stencil", "rectangle", "ellipse"])
    stencil = StringField(choices=stencil_registry.choices, max_length=128)
    # Title
    title = StringField()
    title_position = StringField()
    # Size
    width = IntField()
    height = IntField()
    # default options
    collapsed = BooleanField()
    #
    status_filter: List[AlarmFilter] = EmbeddedDocumentListField(AlarmFilter)
    # Link to other map
    portal_generator = StringField()
    portal_id = StringField()
    map_portal = ObjectIdField()

    NODE_TYPE_MODEL = {
        "managedobject": ManagedObject,
        "objectgroup": ResourceGroup,
        "objectsegment": NetworkSegment,
        "container": Object,
        "cpe": CPE,
    }

    def __str__(self):
        return f"{self.node_type}:{self.object_filter}"

    def __hash__(self):
        return hash(self.node_id)

    @property
    def id(self):
        if self.node_type == "managedobject":
            return str(self.object.id)
        return str(self.node_id)

    @property
    def object(self):
        if self.node_type == "other":
            return None
        if self.node_type == "managedobject" and self.object_filter.managed_object:
            return self.object_filter.managed_object
        if self.node_type == "objectgroup" and self.object_filter.resource_group:
            return self.object_filter.resource_group
        if self.node_type == "objectsegment" and self.object_filter.segment:
            return self.object_filter.segment
        if self.node_type == "cpe" and self.object_filter.cpe:
            return self.object_filter.cpe
        if self.node_type == "container" and self.object_filter.container:
            return self.object_filter.container
        return None

    @property
    def portal(self) -> Optional[Portal]:
        if self.map_portal:
            return Portal(generator="configured", id=str(self.map_portal))
        elif self.node_type == "objectgroup":
            return Portal(generator="objectgroup", id=str(self.object_filter.resource_group.id))
        elif self.node_type == "objectsegment":
            return Portal(generator="segment", id=str(self.object_filter.segment.id))
        elif self.node_type == "container":
            return Portal(generator="container", id=str(self.object_filter.container.id))
        elif self.node_type == "other" and self.portal_generator:
            return Portal(
                generator=self.portal_generator,
                id=self.portal_id,
                settings=self.get_generator_settings(),
            )
        return None

    def get_topology_node(self) -> TopologyNode:
        if self.object:
            n: TopologyNode = self.object.get_topology_node()
        else:
            n = TopologyNode(
                id=str(self.id),
                title=self.title or "",
                type=self.node_type,
            )
        if self.stencil:
            n.stencil = self.stencil
        if self.title:
            n.title = self.title
        if self.parent:
            n.parent = str(self.parent)
        if self.object_filter:
            n.object_filter = self.get_generator_settings()
        return n

    def get_generator_settings(self) -> Optional[Dict[str, str]]:
        r = {}
        if not self.object_filter:
            return r
        if self.object_filter.segment:
            r["segment"] = str(self.object_filter.segment.id)
        if self.object_filter.resource_group:
            r["resource_group"] = str(self.object_filter.resource_group.id)
        if self.object_filter.container:
            r["container"] = str(self.object_filter.container.id)
        return r

    def clean(self):
        from noc.inv.models.mapsettings import MapSettings

        if self.map_portal:
            self.portal_id = str(self.map_portal)
        elif self.portal_generator and not self.portal_id:
            # New settings
            gen = topo_loader[self.portal_generator](**self.get_generator_settings())
            self.portal_id = str(gen.gen_id)
        settings = MapSettings.ensure_settings(
            self.portal_generator, str(self.portal_id), **self.get_generator_settings()
        )
        # if settings.gen_hints != self.get_generator_settings():
        # changed settings
        settings.save()


class LinkItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    type = StringField(choices=["p2p", "cloud", "aggregate"], default="p2p")
    link = ReferenceField(Link)
    source_node = ObjectIdField()  # node_id
    target_nodes = ListField(ObjectIdField())  # node_id
    color = IntField()
    drawtype = StringField(choices=["solid", "bold", "dotted", "dashed"])


class ConfiguredMap(Document):
    """
    Customer MAC address database
    """

    meta = {
        "collection": "configuredmaps",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["name"],
    }

    name = StringField()
    #
    # layout = StringField(choices=["auto", "manual", "spring", "radial"], default="manual")
    layout = StringField(
        choices=[(x.value, x.name) for x in Layout],
        default="M",
    )
    # Map size
    width = IntField(min_value=0)
    height = IntField(min_value=0)
    background_image = ReferenceField(ImageStore)
    background_opacity = IntField(min_value=0, max_value=100, default=30)
    # Global status filter, may be changed by MapSettings
    status_filter = EmbeddedDocumentListField(AlarmFilter)
    # Add linked Node to map
    add_linked_node = BooleanField(default=True)
    # Add founded system links to map
    add_topology_links = BooleanField(default=False)
    # Add portals to external nodes
    enable_node_portal = BooleanField(default=True)
    nodes: List[NodeItem] = EmbeddedDocumentListField(NodeItem)
    links: List[LinkItem] = EmbeddedDocumentListField(LinkItem)
    # lines

    def __str__(self):
        return self.name

    @classmethod
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["ConfiguredMap"]:
        return ConfiguredMap.objects.filter(id=oid).first()

    def get_node_by_id(self, nid) -> Optional[NodeItem]:
        for n in self.nodes:
            if n.id == nid:
                return n
        return
