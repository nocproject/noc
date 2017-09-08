# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import threading
import operator
import uuid
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, UUIDField
from mongoengine.errors import NotUniqueError
import cachetools
# NOC modules
from .vendor import Vendor
from noc.lib.nosql import PlainReferenceField
from noc.core.bi.decorator import bi_sync
from noc.lib.prettyjson import to_json

id_lock = threading.Lock()


@bi_sync
class Platform(Document):
    meta = {
        "collection": "noc.platforms",
        "strict": False,
        "json_collection": "inv.platforms",
        "json_unique_fields": ["vendor", "name"],
        "indexes": [
            {
                "fields": ["vendor", "name"],
                "unique": True
            }
        ]
    }
    vendor = PlainReferenceField(Vendor)
    name = StringField()
    description = StringField(required=False)
    # Full name, combined from vendor platform
    full_name = StringField()
    # Global ID
    uuid = UUIDField(binary=True)
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _ensure_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    def clean(self):
        self.full_name = "%s %s" % (self.vendor.name, self.name)
        super(Platform, self).clean()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Platform.objects.filter(id=id).first()

    def to_json(self):
        return to_json({
            "$collection": self._meta["json_collection"],
            "vendor__name": self.vendor.name,
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description
        }, order=["vendor__name", "name", "uuid", "description"])

    def get_json_path(self):
        return os.path.join(self.vendor.code,
                            "%s.json" % self.code)

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_ensure_cache"),
        key=lambda s, v, n: "%s-%s" % (v.id, n),
        lock=lambda _: id_lock)
    def ensure_platform(cls, vendor, name):
        """
        Get or create platform by vendor and code
        :param vendor:
        :param name:
        :return:
        """
        while True:
            platform = Platform.objects.filter(
                vendor=vendor.id,
                name=name
            ).first()
            if platform:
                return platform
            try:
                platform = Platform(
                    vendor=vendor,
                    name=name,
                    uuid=uuid.uuid4()
                )
                platform.save()
                return platform
            except NotUniqueError:
                pass  # Already created by concurrent process, reread
