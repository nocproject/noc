# ----------------------------------------------------------------------
# ExtStorage model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
from typing import Optional, Union
import operator

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField
from fs import open_fs
from fs.errors import FSError
import cachetools
from bson import ObjectId

# NOC modules
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


@on_delete_check(
    check=[
        ("sa.ManagedObjectProfile", "config_mirror_storage"),
        ("sa.ManagedObjectProfile", "beef_storage"),
        ("sa.ManagedObjectProfile", "config_download_storage"),
    ]
)
class ExtStorage(Document):
    meta = {"collection": "extstorages", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    url = StringField()
    description = StringField()
    type = StringField(
        choices=[
            ("config_mirror", "Config Mirror"),
            ("config_upload", "Config Upload"),
            ("beef", "Beef"),
            ("beef_test", "Beef Test"),
            ("beef_test_config", "Beef Test Config"),
        ]
    )

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    Error = FSError

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ExtStorage"]:
        return ExtStorage.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return ExtStorage.objects.filter(name=name).first()

    def open_fs(self):
        return open_fs(self.url)

    @property
    def is_config_mirror(self):
        return self.type == "config_mirror"

    @property
    def is_beef(self):
        return self.type == "beef"

    @property
    def is_beef_test(self):
        return self.type == "beef_test"

    @property
    def is_beef_test_config(self):
        return self.type == "beef_test_config"
