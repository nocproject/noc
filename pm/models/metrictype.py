# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MetricType model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import os
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, UUIDField, ObjectIdField,
                                LongField)
import cachetools
# NOC Modules
from .metricscope import MetricScope
from noc.inv.models.capability import Capability
from noc.lib.nosql import PlainReferenceField
from noc.main.models.doccategory import category
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json
from noc.core.defer import call_later
from noc.core.model.decorator import on_save
from noc.core.bi.decorator import bi_sync

id_lock = Lock()


@on_save
@bi_sync
@category
class MetricType(Document):
    meta = {
        "collection": "noc.metrictypes",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.metrictypes",
        "json_depends_on": [
            "pm.metricscopes"
        ],
        "json_unique_fields": ["name"]
    }

    # Metric type name, i.e. Interface | Load | In
    name = StringField(unique=True)
    # Global ID
    uuid = UUIDField(binary=True)
    # Metric scope reference
    scope = PlainReferenceField(MetricScope)
    # Database field name
    field_name = StringField()
    # Database field type
    field_type = StringField(
        choices=[
            ("UInt8", "UInt8"),
            ("Int8", "Int8"),
            ("UInt16", "UInt16"),
            ("Int16", "Int16"),
            ("UInt32", "UInt32"),
            ("Int32", "Int32"),
            ("UInt64", "UInt64"),
            ("Int64", "Int64"),
            ("Float32", "Float32"),
            ("Float64", "Float64"),
            ("String", "String")
        ]
    )
    # Text description
    description = StringField(required=False)
    # Measure name, like 'kbit/s'
    # Compatible to Grafana
    measure = StringField()
    # Optional required capability
    required_capability = PlainReferenceField(Capability)
    # Object id in BI, used for counter context hashing
    bi_id = LongField(unique=True)
    #
    category = ObjectIdField()

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "scope__name": self.scope.name,
            "field_name": self.field_name,
            "field_type": self.field_type,
            "description": self.description,
            "measure": self.measure
        }
        if self.required_capability:
            r["required_capability__name"] = self.required_capability.name
        return r

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name", "$collection",
                "uuid", "scope__name", "field_name", "field_type",
                "description", "measure", "vector_tag"])

    def get_json_path(self):
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return MetricType.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return MetricType.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return MetricType.objects.filter(bi_id=id).first()

    def on_save(self):
        call_later(
            "noc.core.clickhouse.ensure.ensure_all_pm_scopes",
            scheduler="scheduler",
            delay=30
        )

    def clean_value(self, value):
        return getattr(self, "clean_%s" % self.field_type)(value)

    @staticmethod
    def clean_UInt8(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 255:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int8(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -127 or v > 127:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt16(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 65535:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int16(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -32767 or v > 32767:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt32(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 4294967295:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int32(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -2147483647 or v > 2147483647:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_UInt64(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < 0 or v > 18446744073709551615:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Int64(value):
        try:
            v = int(value)
        except ValueError:
            raise
        if v < -9223372036854775807 or v > 9223372036854775807:
            raise ValueError("Value out of range")
        return v

    @staticmethod
    def clean_Float32(value):
        return float(value)

    @staticmethod
    def clean_Float64(value):
        return float(value)

    @staticmethod
    def clean_String(value):
        return str(value)
