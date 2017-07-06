# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Profile
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
from noc.core.bi.decorator import bi_sync
from noc.lib.prettyjson import to_json

id_lock = threading.Lock()


@bi_sync
class Profile(Document):
    meta = {
        "collection": "noc.profiles",
        "allow_inheritance": False,
        "json_collection": "inv.profiles"
    }
    name = StringField()
    description = StringField(required=False)
    # Global ID
    uuid = UUIDField(binary=True)
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Profile.objects.filter(id=id).first()

    def to_json(self):
        return to_json({
            "$collection": self._meta["json_collection"],
            "name": self.name,
            "uuid": self.uuid,
            "description": self.description
        }, order=["name", "uuid", "description"])

    def get_json_path(self):
        vendor, soft = self.name.split(".")
        return os.path.join(vendor, "%s.json" % soft)
