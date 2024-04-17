# ---------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import threading
from typing import Optional, Union
import operator
import uuid
import datetime

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, UUIDField, ListField
from mongoengine.queryset import Q
from mongoengine import signals
from pymongo.collection import ReturnDocument
import cachetools
from bson.int64 import Int64

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, DateField
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync, new_bi_id
from noc.core.prettyjson import to_json
from noc.core.change.decorator import change
from noc.models import get_model
from noc.main.models.label import Label
from .vendor import Vendor

id_lock = threading.Lock()

MAX_PLATFORM_LENGTH = 200


@Label.model
@bi_sync
@change
@on_delete_check(
    check=[
        ("sa.ManagedObject", "platform"),
        ("inv.FirmwarePolicy", "platform"),
    ],
    clean_lazy_labels="platform",
)
class Platform(Document):
    meta = {
        "collection": "noc.platforms",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.platforms",
        "json_unique_fields": [("vendor", "name")],
        "indexes": [
            {"fields": ["vendor", "name"], "unique": True},
            ("vendor", "aliases"),
            "labels",
        ],
    }
    vendor = PlainReferenceField(Vendor)
    name = StringField(max_length=MAX_PLATFORM_LENGTH)
    description = StringField(required=False)
    # Full name, combined from vendor platform
    full_name = StringField(unique=True)
    # Platform start of sale date
    start_of_sale = DateField()
    # Platform end of sale date
    end_of_sale = DateField()
    # Platform end of support date
    end_of_support = DateField()
    # End of extended support date (installation local)
    end_of_xsupport = DateField()
    # SNMP OID value
    # sysObjectID.0
    snmp_sysobjectid = StringField(regex=r"^1.3.6(\.\d+)+$")
    # Global ID
    uuid = UUIDField(binary=True)
    # Platform aliases
    aliases = ListField(StringField())
    # Labels
    labels = ListField(StringField())
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(1000, ttl=60)
    _ensure_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self):
        return self.full_name

    def clean(self):
        self.full_name = "%s %s" % (self.vendor.name, self.name)
        if self.aliases:
            self.aliases = sorted(a for a in self.aliases if a != self.name)
        super().clean()

    def save(self, *args, **kwargs):
        to_merge_aliases = not hasattr(self, "_changed_fields") or "aliases" in self._changed_fields
        super().save(*args, **kwargs)
        if to_merge_aliases:
            for a in self.aliases:
                if a == self.name:
                    continue
                self.merge_platform(a)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Platform"]:
        return Platform.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Platform"]:
        return Platform.objects.filter(bi_id=bi_id).first()

    def to_json(self) -> str:
        r = {
            "$collection": self._meta["json_collection"],
            "vendor__code": self.vendor.code[0],
            "name": self.name,
            "uuid": self.uuid,
        }
        if self.aliases:
            r["aliases"] = [str(x) for x in self.aliases]
        if self.description:
            r["description"] = self.description
        if self.start_of_sale:
            r["start_of_sale"] = self.start_of_sale.strftime("%Y-%m-%d")
        if self.end_of_sale:
            r["end_of_sale"] = self.end_of_sale.strftime("%Y-%m-%d")
        if self.end_of_support:
            r["end_of_support"] = self.end_of_support.strftime("%Y-%m-%d")
        if self.snmp_sysobjectid:
            r["snmp_sysobjectid"] = self.snmp_sysobjectid
        if self.labels:
            r["labels"] = self.labels
        return to_json(
            r,
            order=[
                "vendor__code",
                "name",
                "$collection",
                "uuid",
                "aliases",
                "description",
                "start_of_sale",
                "end_of_sale",
                "end_of_support",
                "snmp_sysobjectid",
                "labels",
            ],
        )

    def get_json_path(self) -> str:
        return os.path.join(self.vendor.code[0], "%s.json" % self.name.replace("/", "_"))

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_ensure_cache"),
        key=lambda c, v, n, strict=False, labels=None: f"{v.id}-{n}",
        lock=lambda _: id_lock,
    )
    def ensure_platform(cls, vendor, name, strict=False, labels=None):
        """
        Get or create platform by vendor and code
        :param vendor:
        :param name:
        :param strict: Return None if platform is not found
        :param labels: List of platform labels
        :return:
        """
        # Try to find platform
        q = Q(vendor=vendor.id, name=name) | Q(vendor=vendor.id, aliases=name)
        platform = Platform.objects.filter(q).first()
        if platform or strict:
            return platform
        # Try to create
        if len(name) > MAX_PLATFORM_LENGTH:
            return
        labels = labels or []
        pu = uuid.uuid4()
        d = Platform._get_collection().find_one_and_update(
            {"vendor": vendor.id, "name": name},
            {
                "$setOnInsert": {
                    "uuid": pu,
                    "full_name": "%s %s" % (vendor.name, name),
                    "bi_id": Int64(new_bi_id()),
                    "aliases": [],
                    "labels": labels,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        d["id"] = d["_id"]
        del d["_id"]
        p = Platform(**d)
        signals.post_save.send(cls, document=p, created=True)
        p._clear_changed_fields()
        p._created = False
        return p

    @property
    def is_end_of_sale(self):
        """
        Check if platform reached end-of-sale mark
        :return:
        """
        if not self.end_of_sale:
            return False
        return datetime.date.today() > self.end_of_sale

    @property
    def is_end_of_support(self):
        """
        Check if platform reached end-of-support mark
        :return:
        """
        deadline = []
        if self.end_of_support:
            deadline += [self.end_of_support]
        if self.end_of_xsupport:
            deadline += [self.end_of_xsupport]
        if deadline:
            return datetime.date.today() > max(deadline)
        else:
            return False

    def merge_platform(self, alias):
        """
        Merge *alias* platform
        :param alias: platform name
        :return:
        """
        ap = Platform.objects.filter(vendor=self.vendor.id, name=alias).first()
        if not ap:
            return
        # Replace ce platform
        refs = self._on_delete["check"] + self._on_delete["clean"] + self._on_delete["delete"]
        for model_name, field in refs:
            model = get_model(model_name)
            for obj in model.objects.filter(**{field: ap.id}):
                setattr(obj, field, self)
                obj.save()
        # Finally delete aliases platform
        ap.delete()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_platform")

    @classmethod
    def iter_lazy_labels(cls, platform: "Platform"):
        yield f"noc::platform::{platform.name}::="
