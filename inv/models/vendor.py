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
import six
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
        "auto_create_index": False,
        "json_collection": "inv.vendors",
        "json_unique_fields": ["name"]
    }
    # Short vendor name, included as first part of platform
    name = StringField(unique=True)
    # Full vendor name
    full_name = StringField(unique=True)
    # Unique id
    uuid = UUIDField(binary=True)
    # List of vendor codes to be searched via .get_by_code()
    code = ListField(StringField(), unique=True)
    # Vendor's site
    site = URLField(required=False)
    # Object id in BI
    bi_id = LongField()

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _codes_cache = cachetools.TTLCache(1000, ttl=60)
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
        return Vendor.objects.filter(code=code).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"),
                             lock=lambda _: id_lock)
    def get_by_code(cls, code):
        return cls._get_by_code(code)

    def clean(self):
        # Convert code to list
        if isinstance(self.code, six.string_types):
            self.code = [self.code]
        # Uppercase code
        self.code = [c.upper() for c in self.code]
        # Fill full name if not set
        if not self.full_name:
            self.full_name = self.name
        #
        super(Vendor, self).clean()

    def to_json(self):
        return to_json({
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "full_name":self.full_name,
            "code": self.code,
            "site": self.site,
            "uuid": self.uuid
        }, order=["name", "uuid", "full_name", "code", "site"])

    def get_json_path(self):
        return "%s.json" % self.name

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
            try:
                vendor = Vendor(
                    name=code,
                    full_name=code,
                    code=[code],
                    uuid=uuid.uuid4()
                )
                vendor.save()
                return vendor
            except NotUniqueError:
                pass  # Already created by concurrent process, reread
