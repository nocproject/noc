# ----------------------------------------------------------------------
# MACBlacklist model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from collections import namedtuple
from typing import List

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    UUIDField,
    ListField,
    EmbeddedDocumentField,
)
import cachetools

# NOC modules
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.core.mongo.fields import PlainReferenceField
from noc.core.prettyjson import to_json
from noc.core.mac import MAC

_list_lock = Lock()
ListItem = namedtuple("ListItem", ["from_mac", "to_mac", "is_duplicated"])


class MACBlacklistAffected(EmbeddedDocument):
    vendor = PlainReferenceField(Vendor)
    platform = PlainReferenceField(Platform)

    def __str__(self):
        if self.platform:
            return "%s:%s" % (self.vendor.name, self.platform.name)
        return self.vendor.name

    def to_json(self) -> str:
        r = {"vendor__code": self.vendor.code}
        if self.platform:
            r["platform__name"] = self.platform.name
        return r


class MACBlacklist(Document):
    meta = {
        "collection": "macblacklist",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.macblacklist",
        "json_depends_on": ["inv.vendor", "inv.platform"],
    }

    name = StringField(unique=True)
    # Unique id
    uuid = UUIDField(binary=True)
    #
    from_mac = StringField()
    to_mac = StringField()
    description = StringField()
    affected = ListField(EmbeddedDocumentField(MACBlacklistAffected))
    is_duplicated = BooleanField(default=False)
    is_ignored = BooleanField(default=False)

    _list_cache = cachetools.TTLCache(100, ttl=60)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        self.from_mac = str(MAC(self.from_mac))
        self.to_mac = str(MAC(self.to_mac))
        if self.from_mac > self.to_mac:
            self.from_mac, self.to_mac = self.to_mac, self.from_mac

    def to_json(self) -> str:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "from_mac": self.from_mac,
            "to_mac": self.to_mac,
            "affected": [a.to_json() for a in self.affected],
            "is_duplicated": self.is_duplicated,
            "is_ignored": self.is_ignored,
        }
        if self.description:
            r["description"] = self.description
        return to_json(
            r,
            order=[
                "name",
                "uuid",
                "from_mac",
                "to_mac",
                "description",
                "is_duplicated",
                "affected",
            ],
        )

    def get_json_path(self) -> str:
        return "%s.json" % self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_list_cache"), lock=lambda _: _list_lock)
    def _get_blacklist(cls) -> List[ListItem]:
        return [
            ListItem(from_mac=MAC(d.from_mac), to_mac=MAC(d.to_mac), is_duplicated=d.is_duplicated)
            for d in cls.objects.all()
        ]

    @classmethod
    def is_banned_mac(cls, mac: str, is_duplicated: bool = False, is_ignored: bool = False) -> bool:
        """
        Check if mac is banned for specified reason
        Args:
            mac:
            is_duplicated: Check MAC is duplicated flag
            is_ignored: Check MAC is ignored flag
        """
        m = MAC(mac)
        for item in cls._get_blacklist():
            if item.from_mac <= m <= item.to_mac:
                if is_duplicated and item.is_duplicated:
                    return True
                if is_ignored and item.is_duplicated:
                    return True
        return False
