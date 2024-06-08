# ---------------------------------------------------------------------
# Vendor model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
from typing import Optional, Union
import operator
import uuid

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, URLField, UUIDField, ListField
from mongoengine.errors import NotUniqueError
import cachetools

# NOC modules
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check, on_save
from noc.core.change.decorator import change
from noc.core.bi.decorator import bi_sync

id_lock = threading.Lock()


@bi_sync
@on_save
@change
@on_delete_check(
    check=[
        ("inv.ObjectModel", "vendor"),
        ("inv.Platform", "vendor"),
        ("inv.Firmware", "vendor"),
        ("sa.ManagedObject", "vendor"),
    ],
    clean_lazy_labels="vendor",
)
class Vendor(Document):
    """
    Equipment vendor
    """

    meta = {
        "collection": "noc.vendors",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.vendors",
        "json_unique_fields": ["name", "code"],
    }
    # Short vendor name, included as first part of platform
    name = StringField(unique=True)
    # Full vendor name
    full_name = StringField()
    # Unique id
    uuid = UUIDField(binary=True)
    # List of vendor codes to be searched via .get_by_code()
    code = ListField(StringField(), unique=True)
    # Vendor's site
    site = URLField(required=False)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(1000, ttl=60)
    _code_cache = cachetools.TTLCache(1000, ttl=60)
    _ensure_cache = cachetools.TTLCache(1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Vendor"]:
        return Vendor.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["Vendor"]:
        return Vendor.objects.filter(bi_id=bi_id).first()

    @classmethod
    def _get_by_code(cls, code):
        """
        Uncached version of get_by_code
        :param code:
        :return:
        """
        code = code.upper()
        return Vendor.objects.filter(code=code).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code):
        return cls._get_by_code(code)

    def clean(self):
        # Convert code to list
        if isinstance(self.code, str):
            self.code = [self.code]
        # Uppercase code
        self.code = [c.upper() for c in self.code]
        # Fill full name if not set
        if not self.full_name:
            self.full_name = self.name
        #
        super().clean()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "name" in self._changed_fields:
            from .platform import Platform

            for p in Platform.objects.filter(vendor=self.id):
                p.save()  # Rebuild full name

    def to_json(self) -> str:
        return to_json(
            {
                "name": self.name,
                "$collection": self._meta["json_collection"],
                "full_name": self.full_name,
                "code": self.code,
                "site": self.site,
                "uuid": self.uuid,
            },
            order=["name", "uuid", "full_name", "code", "site"],
        )

    def get_json_path(self) -> str:
        return "%s.json" % self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ensure_cache"), lock=lambda _: id_lock)
    def ensure_vendor(cls, code):
        """
        Get or create vendor by code
        :param code:
        :return:
        """
        # Try to get cached version
        vendor = Vendor._get_by_code(code)
        if vendor:
            return vendor
        # Not found, try to create
        try:
            vendor = Vendor(name=code, full_name=code, code=[code], uuid=uuid.uuid4())
            vendor.save()
            return vendor
        except NotUniqueError:
            # Already created by concurrent process,
            # reread cached version
            vendor = Vendor._get_by_code(code)
            if vendor:
                return vendor
            raise ValueError("Vendor without code")

    @classmethod
    def iter_lazy_labels(cls, vendor: "Vendor"):
        yield f"noc::vendor::{vendor.name}::="
