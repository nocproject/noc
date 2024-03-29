# ----------------------------------------------------------------------
# TechDomain
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Dict, Any, Union
import operator
from enum import Enum

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    IntField,
    EmbeddedDocumentListField,
    UUIDField,
    BooleanField,
)

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.main.models.handler import Handler
from noc.core.mongo.fields import PlainReferenceField

id_lock = Lock()


class DiscriminatorItem(EmbeddedDocument):
    """
    Tech domain discriminator.

    Attributes:
        name: Discriminator name.
        description: Discriminator description.
        is_required: Discriminator is required on endpoint.
    """

    name = StringField()
    description = StringField()
    is_required = BooleanField()

    def __str__(self) -> str:
        return self.name

    @property
    def json_data(self) -> Dict[str, Any]:
        r: Dict[str, Any] = {"name": self.name}
        if self.description:
            r["description"] = self.description
        r["is_required"] = self.is_required
        return r


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


@bi_sync
@on_delete_check(check=[("inv.Endpoint", "tech_domain")])
class TechDomain(Document):
    """
    Technological Domain.

    Represents a single techology which
    provides endpoints to the channels
    and hides an internal structure.

    Attributes:
        name: Human-readable name.
        uuid: Collection uuid.
        description: Optional descirption.
        uuid: UUID.
        description: Optional description.
        discriminators: List of available discriminators.
        max_endpoints: Limit maximal amount of endpoints, when set.
        full_mesh: Bidirectional, if set.
        require_unique: Endpoints must have discriminators.
        bi_id: Bi-encoded id.
    """

    meta = {
        "collection": "techdomains",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.techdomains",
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    kind = StringField(choices=[x.value for x in ChannelKind])
    discriminators = EmbeddedDocumentListField(DiscriminatorItem)
    max_endpoints = IntField(required=False)
    full_mesh = BooleanField()
    require_unique = BooleanField()
    controller_handler = PlainReferenceField(Handler, required=False)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(bi_id=bi_id).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r: Dict[str, Any] = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
        }
        if self.description:
            r["description"] = self.description
        if self.max_endpoints is not None:
            r["max_endpoints"] = self.max_endpoints
        r["full_mesh"] = self.full_mesh
        r["require_unique"] = self.require_unique
        if self.discriminators:
            r["discriminators"] = [d.json_data for d in self.discriminators]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "$collection", "uuid", "description"],
        )

    def get_json_path(self) -> str:
        return f"{quote_safe_path(self.name)}.json"
