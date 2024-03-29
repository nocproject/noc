# ----------------------------------------------------------------------
# Channel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union, Dict, Any
import operator
from enum import Enum

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, ListField, BooleanField

# NOC modules
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.project.models.project import Project
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


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
@on_delete_check(check=[("inv.Endpoint", "channel")])
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
    project = ForeignKeyField(Project)
    supplier = PlainReferenceField(Supplier)
    subscriber = PlainReferenceField(Subscriber)
    is_free = BooleanField()
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = PlainReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self) -> str:
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Channel"]:
        return Channel.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Channel"]:
        return Channel.objects.filter(bi_id=bi_id).first()
