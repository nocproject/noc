# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import operator
import uuid
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, LongField, URLField,
                                UUIDField, ListField)
from mongoengine.errors import NotUniqueError
import cachetools
# NOC modules
from noc.lib.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync

id_lock = threading.Lock()


@bi_sync
@on_delete_check(check=[
    ("inv.ObjectModel", "vendor"),
    ("inv.Platform", "vendor"),
    ("inv.Firmware", "vendor"),
    ("sa.ManagedObject", "vendor")
])
class Vendor(Document):
    """
    Equipment vendor
    """
    meta = {
        "collection": "noc.vendors",
        "strict": False,
        "json_collection": "inv.vendors",
        "json_unique_fields": ["code"]
    }

    name = StringField(unique=True)
    code = StringField(unique=True)
    site = URLField(required=False)
    uuid = UUIDField(binary=True)
    aliases = ListField(StringField())
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _code_cache = cachetools.TTLCache(1000, ttl=60)
    _ensure_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Vendor.objects.filter(id=id).first()

    @classmethod
    def _get_by_code(cls, code):
        """
        Uncached version of get_by_code
        :param code:
        :return:
        """
        code = code.upper()
        vendor = Vendor.objects.filter(code=code).first()
        if vendor:
            return vendor
        return Vendor.objects.filter(aliases=code).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"),
                             lock=lambda _: id_lock)
    def get_by_code(cls, code):
        return cls._get_by_code(code)

    def to_json(self):
        return to_json({
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "code": self.code,
            "site": self.site,
            "uuid": self.uuid,
            "aliases": self.aliases
        }, order=["name", "uuid", "code", "site", "aliases"])

    def get_json_path(self):
        return "%s.json" % self.code

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_ensure_cache"),
                             lock=lambda _: id_lock)
    def ensure_vendor(cls, code):
        """
        Get or create vendor by code
        :param code:
        :return:
        """
        while True:
            vendor = Vendor._get_by_code(code)
            if vendor:
                return vendor
            code = code.upper()
            try:
                vendor = Vendor(
                    name=code,
                    code=code,
                    uuid=uuid.uuid4()
                )
                vendor.save()
                return vendor
            except NotUniqueError:
                pass  # Already created by concurrent process, reread
