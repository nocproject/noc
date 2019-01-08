# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import threading
import operator
import uuid
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, LongField, UUIDField, ListField
from mongoengine.queryset import Q
from pymongo.collection import ReturnDocument
import cachetools
from bson.int64 import Int64
# NOC modules
from noc.lib.nosql import PlainReferenceField, DateField
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync, new_bi_id
from noc.lib.prettyjson import to_json
from noc.models import get_model
from .vendor import Vendor

id_lock = threading.Lock()


@bi_sync
@on_delete_check(check=[
    ("sa.ManagedObject", "platform"),
    ("sa.ManagedObjectSelector", "filter_platform"),
    ("inv.FirmwarePolicy", "platform")
])
class Platform(Document):
    meta = {
        "collection": "noc.platforms",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "inv.platforms",
        "json_unique_fields": [("vendor", "name")],
        "indexes": [
            {
                "fields": ["vendor", "name"],
                "unique": True
            },
            ("vendor", "aliases")
        ]
    }
    vendor = PlainReferenceField(Vendor)
    name = StringField()
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
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(1000, ttl=60)
    _ensure_cache = cachetools.TTLCache(1000, ttl=60)

    def __unicode__(self):
        return self.full_name

    def clean(self):
        self.full_name = "%s %s" % (self.vendor.name, self.name)
        if self.aliases:
            self.aliases = sorted(a for a in self.aliases if a != self.name)
        super(Platform, self).clean()

    def save(self, *args, **kwargs):
        to_merge_aliases = not hasattr(self, "_changed_fields") or "aliases" in self._changed_fields
        super(Platform, self).save(*args, **kwargs)
        if to_merge_aliases:
            for a in self.aliases:
                if a == self.name:
                    continue
                self.merge_platform(a)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Platform.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return Platform.objects.filter(bi_id=id).first()

    def to_json(self):
        r = {
            "$collection": self._meta["json_collection"],
            "vendor__name": self.vendor.name,
            "name": self.name,
            "uuid": self.uuid
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
        return to_json(r, order=[
            "vendor__name", "name", "$collection", "uuid", "aliases",
            "description", "start_of_sale", "end_of_sale", "end_of_support",
            "snmp_sysobjectid"])

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
        # Try to find platform
        q = Q(vendor=vendor.id, name=name) | Q(vendor=vendor.id, aliases=name)
        platform = Platform.objects.filter(q).first()
        if platform:
            return platform
        # Try to create
        pu = uuid.uuid4()
        d = Platform._get_collection().find_one_and_update({
            "vendor": vendor.id,
            "name": name
        }, {
            "$setOnInsert": {
                "uuid": pu,
                "full_name": "%s %s" % (vendor.name, name),
                "bi_id": Int64(new_bi_id()),
                "aliases": []
            }
        }, upsert=True, return_document=ReturnDocument.AFTER)
        d["id"] = d["_id"]
        del d["_id"]
        p = Platform(**d)
        p._changed_fields = []
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
