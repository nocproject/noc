# ----------------------------------------------------------------------
# Protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import os
import operator
from dataclasses import dataclass
from threading import Lock
from typing import Optional, Iterable, List, Any, Dict, Union

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.queryset.base import NULLIFY
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    LongField,
    EmbeddedDocumentListField,
    UUIDField,
    DynamicField,
    IntField,
    ListField,
    ReferenceField,
)

# from mongoengine.errors import ValidationError

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.discriminator import (
    discriminator,
    scopes,
    LambdaDiscriminator,
    VlanDiscriminator,
    OduDiscriminator,
)
from noc.inv.models.technology import Technology
from noc.core.protodcsources.base import BaseDiscriminatorSource

id_lock = Lock()

PROTOCOL_DIRECTION_CODES = {">", "<", "*"}
rx_mode = re.compile(r"^(.+?)\s*\((.+)\)")


@dataclass(frozen=True)
class ProtocolVariant(object):
    """
    Add __contains__ for connection check
    """

    protocol: "Protocol"
    direction: str = "*"
    discriminator: str | None = None
    data: dict[str, str] | None = None
    modes: list[str] | None = None

    def __str__(self) -> str:
        return self.code

    def __eq__(self, other: "ProtocolVariant") -> bool:
        r = self.protocol.id == other.protocol.id and self.direction == other.direction
        if not self.discriminator:
            return r
        return r and self.discriminator == other.discriminator

    def __contains__(self, item: "ProtocolVariant") -> bool:
        if self.protocol.id != item.protocol.id or self.direction != item.direction:
            return False
        if (self.discriminator and not item.discriminator) or (
            not self.discriminator and item.discriminator
        ):
            return False
        return self.discriminator == item.discriminator

    def __hash__(self):
        return hash(self.code)

    @property
    def code(self) -> str:
        if not self.discriminator and self.direction == "*":
            return self.protocol.code
        elif not self.discriminator:
            return f"{self.direction}{self.protocol.code}"
        return f"{self.direction}::{self.protocol.code}::{self.discriminator}"

    @classmethod
    def get_by_code(cls, code: str) -> "ProtocolVariant":
        """
        Generate Protocol Variant by code
        LLDP -> LLDP
        >LLDP > LLDP, >
        >::LLDP > LLDP, >
        :param code:
        :return:
        """
        # d_code, *x = code.split("::")
        # vd_code = None  # Variant Discriminator Code
        if code[0] in PROTOCOL_DIRECTION_CODES:
            d_code, p_code = code[0], code[1:]
        else:
            d_code, p_code = "*", code
        # Split modes
        match = rx_mode.match(p_code)
        if match:
            p_code, m = match.groups()
            modes = [x.strip() for x in m.split(",")]
        else:
            modes = None
        #
        p_code, *vd_code = p_code.strip("::").split("::")
        # Detect Protocol Code
        if len(vd_code) > 1:
            raise ValueError("Unknown variant format: %s" % code)
        elif vd_code:
            vd_code = vd_code[0]
        #
        protocol = Protocol.get_by_code(p_code)
        if not protocol and "-" in p_code:
            # Old format
            p_code, vd_code = p_code.rsplit("-", 1)
            protocol = Protocol.get_by_code(p_code)
        if not protocol:
            msg = f"Unknown protocol code: {p_code}"
            raise ValueError(msg)
        return ProtocolVariant(protocol, d_code, vd_code, modes=modes)

    def get_discriminator(
        self,
    ) -> Optional[Union[LambdaDiscriminator, OduDiscriminator, VlanDiscriminator]]:
        if not self.protocol.discriminator:
            return None
        if self.protocol.discriminator != "loader":
            return discriminator(
                f"{self.protocol.discriminator}::{self.discriminator or self.protocol.discriminator_default}"
            )
        ds = self.protocol.get_discriminator_source(self.data)
        return ds.get_discriminator_instance(self.discriminator)


class ProtocolAttr(EmbeddedDocument):
    interface = StringField()
    attr = StringField()
    value = DynamicField()

    def __str__(self):
        return f"{self.interface}.{self.attr} = {self.value}"

    @property
    def json_data(self) -> Dict[str, Any]:
        return {
            "interface": self.interface,
            "attr": self.attr,
            "value": self.value,
        }


class DiscriminatorAttr(EmbeddedDocument):
    code: str = StringField(required=True)
    limit: int = IntField(default=1)

    def __str__(self):
        return self.code

    @property
    def json_data(self) -> Dict[str, Any]:
        return {"code": self.code, "data": [d.json_data for d in self.data]}


@bi_sync
@on_delete_check(check=[("inv.ObjectModel", "connections__protocols__protocol")])
class Protocol(Document):
    """
    Technology

    Abstraction to restrict ResourceGroup links
    """

    meta = {
        "collection": "protocols",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["code"],
        "json_collection": "inv.protocols",
        "json_unique_fields": ["code", "uuid"],
    }

    #
    name = StringField()
    code = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    technology: "Technology" = PlainReferenceField(Technology)
    data: List["ProtocolAttr"] = EmbeddedDocumentListField(ProtocolAttr)
    connection_schema = StringField(
        choices=[
            ("U", "Unidirectional"),
            ("BO", "Bidirectional over One Connection"),
            ("BD", "Bidirectional over Differ Connection"),
        ],
        default="BD",
    )
    # Discriminators
    discriminator: str = StringField(
        choices=list(scopes) + ["loader"],
        required=False,
    )
    discriminator_loader = StringField(default=None)
    discriminator_default = StringField(default=None)  # Alias table ?
    #
    transport_protocols = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
    # For
    # use_helper
    # helper = StringField()

    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Protocol"]:
        return Protocol.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Protocol"]:
        return Protocol.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code) -> Optional["Protocol"]:
        return Protocol.objects.filter(code=code).first()

    @classmethod
    def _reset_caches(cls, id):
        try:
            del cls._id_cache[str(id),]  # Tuple
        except KeyError:
            pass

    def get_data(self, interface: str, key: str, **kwargs) -> Any:
        for item in self.data:
            if item.interface == interface and item.attr == key:
                return item.value
        return None

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "code": self.code,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "technology__name": self.technology.name,
            "connection_schema": self.connection_schema,
            "data": [c.json_data for c in self.data],
        }
        if self.discriminator:
            r["discriminator"] = self.discriminator
        if self.discriminator_loader:
            r["discriminator_loader"] = self.discriminator_loader
        if self.discriminator_default:
            r["discriminator_default"] = self.discriminator_default
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=["name", "code", "$collection", "uuid", "description", "technology", "data"],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def get_variant_by_code(cls, code: str) -> "ProtocolVariant":
        """
        Return protocol variant by code

        :param code: Protocol Variant code
        """
        return ProtocolVariant.get_by_code(code)

    @property
    def allow_different_connection(self) -> bool:
        return self.connection_schema != "BO"

    def iter_protocol_variants(self) -> Iterable[ProtocolVariant]:
        """
        @todo combinations
        """
        yield ProtocolVariant(self)
        if self.allow_different_connection != "BO":
            yield ProtocolVariant(self, ">")
            yield ProtocolVariant(self, "<")
        if not self.discriminator == "D":
            return
        ds = self.get_discriminator_source()
        for code in ds:
            yield ProtocolVariant(self, "<", code)
            yield ProtocolVariant(self, ">", code)

    def get_discriminator_source(
        self, data: Optional[List[ProtocolAttr]] = None
    ) -> Optional[BaseDiscriminatorSource]:
        from noc.core.protodcsources.loader import loader

        ds = loader[self.discriminator_loader]
        return ds(self, data)
