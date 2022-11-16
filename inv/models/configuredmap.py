# ---------------------------------------------------------------------
# Configured Map
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

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
    node_type = StringField(choices=["group", "managedobject", "segment", "other"])
    reference_id = StringField()
    add_nested = BooleanField()  # Add nested nodes (if supported) all nodes from group or children
    # Draw block
    shape = StringField(choices=["stencil", "rectangle", "ellipse"])
    stencil = StringField(choices=stencil_registry)
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

    @property
    def object(self):
        if self.node_type == "managedobject":
            return ManagedObject.get_by_id(int(self.reference_id))
        if self.node_type == "group":
            return ResourceGroup.get_by_id(self.reference_id)
        if self.node_type == "segment":
            return NetworkSegment.get_by_id(self.reference_id)


class LinkItem(EmbeddedDocument):
    type = StringField(choices=["p2p", "cloud", "parent", "aggregate"], default="p2p")
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
    width = IntField()
    height = IntField()
    background_image = ReferenceField(ImageStore)
    # Global status filter, may be changed by MapSettings
    status_filter = EmbeddedDocumentListField(AlarmFilter)
    # Add linked Node to map
    add_linked_node = BooleanField(default=True)
    # Add founded system links to map
    add_topology_links = BooleanField(default=False)
    # Add portals to external nodes
    enable_node_portal = BooleanField(default=True)
    nodes = EmbeddedDocumentListField(NodeItem)
    links = EmbeddedDocumentListField(LinkItem)
    # lines
