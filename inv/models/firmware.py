# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Firmware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import threading
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, UUIDField
import cachetools
# NOC modules
from .vendor import Vendor
from noc.sa.models.profile import Profile
from noc.lib.nosql import ReferenceField
from noc.core.bi.decorator import bi_sync
from noc.lib.prettyjson import to_json

id_lock = threading.Lock()


@bi_sync
class Firmware(Document):
    meta = {
        "collection": "noc.firmwares",
        "allow_inheritance": False,
        "json_collection": "inv.firmwares",
        "indexes": [
            {
                "fields": ["profile", "vendor", "version"],
                "unique": True
            }
        ]
    }
    # Global ID
    uuid = UUIDField(binary=True)
    #
    profile = ReferenceField(Profile)
    vendor = ReferenceField(Vendor)
    version = StringField()
    description = StringField()
    download_url = StringField()
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Firmware.objects.filter(id=id).first()

    def to_json(self):
        return to_json({
            "$collection": self._meta["json_collection"],
            "profile__name": self.profile.name,
            "vendor__code": self.vendor.code,
            "version": self.version,
            "uuid": self.uuid
        }, order=["profile__name", "vendor__code", "version", "uuid"])

    def get_json_path(self):
        return os.path.join(
            self.vendor.code,
            self.profile.name,
            "%s.json" % self.version.replace(os.sep, "_")
        )
