# ----------------------------------------------------------------------
# Channel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Dict, Any
import operator
from enum import Enum

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListDocumentField,
    UUIDField,
    ReferenceField,
    ListField,
)

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.project.models.project import Project
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.label import Label


id_lock = Lock()


class ChannelKind(Enum):
    """
    Kind of channel.

    Attributes:
        L1: Level-1
        L2: Level-2
        L3: Level-3
        INTERNET: Global connectivity.
    """

    L1 = "l1"
    L2 = "l2"
    L3 = "l3"
    INTERNET = "internet"


class ChannelTopology(Enum):
    """
    Topology of the channel.

    Attributes:
        P2P: Point-to-point.
        P2MP: Point-to-multipoint (unidirectional).
        TREE: Tree.
        STAR: Full mesh.
    """

    P2P = "p2p"
    P2MP = "p2mp"
    TREE = "tree"
    STAR = "star"


@bi_sync
@Label.model
class Channel(Document):
    """
    Channel.
    """

    meta = {
        "collection": "channels",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["effective_labels"],
    }

    name = StringField(unique=True)
    description = StringField()
    kind = StringField(choices=[x.value for x in ChannelKind], required=True)
    topology = StringField(choices=[x.value for x in ChannelTopology], required=True)
    project = ForeignKeyField(Project)
    supplier = ReferenceField(Supplier)
    subscriber = ReferenceField(Subscriber)
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: ObjectId) -> Optional["Channel"]:
        return Channel.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Channel"]:
        return Channel.objects.filter(bi_id=bi_id).first()
