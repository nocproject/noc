# ----------------------------------------------------------------------
# Channel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator


# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    ListField,
    BooleanField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.project.models.project import Project
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.supplier import Supplier
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.decorator import on_delete_check
from noc.core.channel.types import ChannelKind, ChannelTopology
from .techdomain import TechDomain

id_lock = Lock()


class ConstraintItem(EmbeddedDocument):
    """
    Constraint Item.

    Attributes:
        type: Constraint type, include of exclude.
        strict: Generate fault if constraint cannot be met.
        resource: Resource reference.
    """

    type = StringField(choices=["i", "e"])
    strict = BooleanField()
    resource = StringField()


@bi_sync
@Label.model
@on_delete_check(check=[("inv.Channel", "parent"), ("inv.Endpoint", "channel")])
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
    parent = PlainReferenceField("self", allow_blank=True)
    tech_domain = PlainReferenceField(TechDomain)
    description = StringField()
    project = ForeignKeyField(Project)
    supplier = PlainReferenceField(Supplier)
    subscriber = PlainReferenceField(Subscriber)
    kind = StringField(choices=[x.value for x in ChannelKind])
    topology = StringField(choices=[x.value for x in ChannelTopology])
    discriminator = StringField(required=False)
    labels = ListField(StringField())
    effective_labels = ListField(StringField())
    constraints = EmbeddedDocumentListField(ConstraintItem)
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
