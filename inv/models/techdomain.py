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
from noc.core.channel.types import ChannelKind, ChannelTopology

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
        code: Short symbolic code.
        description: Optional descirption.
        uuid: UUID.
        description: Optional description.
        discriminators: List of available discriminators.
        max_endpoints: Limit maximal amount of endpoints, when set.
        allow_parent: Allow parent channels.
        allow_children: Allow nested channels.
        allow_p2p: Allow p2p topology.
        allow_up2p: Allow up2p topology.
        allow_bunch: Allow bunch topology.
        allow_p2mp: Allow p2mp topology.
        allow_up2mp: Allow up2mp topology.
        allow_star: Allow star topology.
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
    code = StringField(unique=True)
    description = StringField()
    kind = StringField(choices=[x.value for x in ChannelKind])
    discriminators = EmbeddedDocumentListField(DiscriminatorItem)
    max_endpoints = IntField(required=False)
    controller_handler = PlainReferenceField(Handler, required=False)
    allow_parent = BooleanField()
    allow_children = BooleanField()
    allow_p2p = BooleanField()
    allow_up2p = BooleanField()
    allow_bunch = BooleanField()
    allow_p2mp = BooleanField()
    allow_up2mp = BooleanField()
    allow_star = BooleanField()
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
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["TechDomain"]:
        return TechDomain.objects.filter(code=code).first()

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
            "code": self.code,
        }
        if self.description:
            r["description"] = self.description
        if self.max_endpoints is not None and self.max_endpoints:
            r["max_endpoints"] = self.max_endpoints
        r.update(
            {
                "allow_parent": self.allow_parent,
                "allow_children": self.allow_children,
                "allow_p2p": self.allow_p2p,
                "allow_up2p": self.allow_up2p,
                "allow_bunch": self.allow_bunch,
                "allow_p2mp": self.allow_p2mp,
                "allow_up2mp": self.allow_up2mp,
                "allow_star": self.allow_star,
            }
        )
        if self.discriminators:
            r["discriminators"] = [d.json_data for d in self.discriminators]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "$collection", "uuid", "description"],
        )

    def get_json_path(self) -> str:
        return f"{quote_safe_path(self.code)}.json"

    def is_allowed_topology(self, topo: ChannelTopology) -> bool:
        """
        Check if topology is allowed.

        Args:
            topo: Channel Topology.

        Returns:
            True: If topology is allowed.
            False: If topology is not allowed.
        """
        return getattr(self, f"allow_{topo.value}")
