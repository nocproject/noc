# ---------------------------------------------------------------------
# Configured Map
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List

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
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.stencil import stencil_registry
from noc.core.topology.types import TopologyNode, Portal
from noc.main.models.imagestore import ImageStore
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.link import Link


class AlarmFilter(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    alarm_class = ListField(ReferenceField(AlarmClass))
    min_severity = AlarmSeverity
    # drawtype
    # color


class NodeItem(EmbeddedDocument):
    node_id = ObjectIdField(default=bson.ObjectId)
    parent = ObjectIdField()
    # Generator Config
    node_type = StringField(choices=["objectgroup", "managedobject", "objectsegment", "other"])
    reference_id = StringField()
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
    status_filter = EmbeddedDocumentListField(AlarmFilter)
    # Link to other map
    map_portal = ObjectIdField()

    NODE_TYPE_MODEL = {
        "managedobject": ManagedObject,
        "objectgroup": ResourceGroup,
        "objectsegment": NetworkSegment,
    }

    def __str__(self):
        return f"{self.node_type}:{self.reference_id}"

    def __hash__(self):
        return hash(self.node_id)

    @property
    def id(self):
        if self.node_type == "managedobject":
            return str(self.object.id)
        return str(self.node_id)

    @property
    def object(self):
        if (
            not self.reference_id
            or self.node_type == "other"
            or self.node_type not in self.NODE_TYPE_MODEL
        ):
            return None
        ref = self.reference_id
        if self.node_type == "managedobject":
            ref = int(ref)
        return self.NODE_TYPE_MODEL[self.node_type].get_by_id(ref)

    @property
    def portal(self) -> Optional[Portal]:
        generator = None
        if self.map_portal:
            return Portal(generator="configured", id=str(self.map_portal))
        if self.node_type == "objectgroup":
            generator = "objectgroup"
        elif self.node_type == "objectsegment":
            generator = "segment"
        if not generator:
            return None
        return Portal(generator=generator, id=str(self.reference_id))

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
        return n


class LinkItem(EmbeddedDocument):
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
    layout = StringField(choices=["auto", "manual", "spring", "radial"], default="manual")
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

    @classmethod
    def get_by_id(cls, id) -> Optional["ConfiguredMap"]:
        return ConfiguredMap.objects.filter(id=id).first()

    def get_node_by_id(self, nid) -> Optional[NodeItem]:
        for n in self.nodes:
            if n.id == nid:
                return n
        return
