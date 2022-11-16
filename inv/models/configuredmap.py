# ---------------------------------------------------------------------
# Configured Map
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
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
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.core.stencil import stencil_registry
from noc.main.models.imagestore import ImageStore
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.link import Link


class AlarmFilter(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    alarm_class = ListField(ReferenceField(AlarmClass))
    min_severity = AlarmSeverity
    # drawtype
    # color


class NodeItem(EmbeddedDocument):
    node_id = ObjectIdField()
    # Generator Config
    node_type = StringField(choices=["group", "managedobject", "other"])
    reference_id = StringField()
    add_nested = BooleanField()  # Add nested nodes (if supported) all nodes from group or children
    # Draw block
    drawtype = StringField(choices=["stencil", "rectangle", "ellipse"])
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


class LinkItem(EmbeddedDocument):
    link = ReferenceField(Link)
    source_node = StringField()  # node_id
    target_node = StringField()  # node_id
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
    # Add portals to external nodes
    enable_node_portal = BooleanField(default=True)
    nodes = EmbeddedDocumentListField(NodeItem)
    links = EmbeddedDocumentListField(LinkItem)
    # lines
