# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ExtStorage model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField
from fs import open_fs
from fs.errors import FSError
import cachetools
# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(check=[
    ("sa.ManagedObjectProfile", "config_mirror_storage"),
    ("sa.ManagedObjectProfile", "beef_storage"),
])
class ExtStorage(Document):
    meta = {
        "collection": "extstorages",
        "strict": False,
        "auto_create_index": False
    }

    name = StringField(unique=True)
    url = StringField()
    description = StringField()
    type = StringField(
        choices=[
            ("config_mirror", "Config Mirror"),
            ("beef", "Beef"),
            ("beef_test", "Beef Test"),
            ("beef_test_config", "Beef Test Config")
        ]
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    Error = FSError

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ExtStorage.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return ExtStorage.objects.filter(name=name).first()

    def open_fs(self):
        return open_fs(self.url)
