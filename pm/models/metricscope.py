# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MetricScope model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, ListField, EmbeddedDocumentField, UUIDField,
    BooleanField)
import cachetools
# NOC Modules
from noc.lib.prettyjson import to_json

id_lock = Lock()


class KeyField(EmbeddedDocument):
    # Table field name
    field_name = StringField()
    # Model reference, i.e. sa.ManagedObject
    model = StringField()

    def __unicode__(self):
        return self.field_name

    def to_json(self):
        return {
            "field_name": self.field_name,
            "model": self.model
        }

    @property
    def field_type(self):
        return "UInt64"


class PathItem(EmbeddedDocument):
    name = StringField()
    is_required = BooleanField()
    # Default value, when empty
    default_value = StringField()

    def __unicode__(self):
        return self.name

    def to_json(self):
        v = {
            "name": self.name,
            "is_required": self.is_required
        }
        if self.default_value:
            v["default_value"] = self.default_value
        return v


class MetricScope(Document):
    meta = {
        "collection": "noc.metricscopes",
        "json_collection": "pm.metricscopes",
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    # Database table name
    table_name = StringField()
    description = StringField(required=False)
    key_fields = ListField(EmbeddedDocumentField(KeyField))
    path = ListField(EmbeddedDocumentField(PathItem))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"),
                             lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return MetricScope.objects.filter(id=id).first()

    @property
    def json_data(self):
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "table_name": self.table_name,
            "description": self.description,
            "key_fields": [kf.json_data() for kf in self.key_fields],
            "path": [p.json_data() for p in self.path]
        }
        return r

    def to_json(self):
        return to_json(
            self.json_data,
            order=[
                "name", "$collection",
                "uuid", "table_name",
                "description",
                "key_fields", "path"])

    def get_json_path(self):
        return "%s.json" % self.name

    def iter_fields(self):
        """
        Yield (field_name, field_type) tuples
        :return:
        """
        from .metrictype import MetricType

        yield ("date", "Date")
        yield ("ts", "DateTime")
        for f in self.key_fields:
            yield (f.field_name, f.field_type)
        if self.path:
            yield ("path", "Array(String)")
        for t in MetricType.objects.filter(scope=self.id).order_by("id"):
            yield (t.field_name, t.field_type)

    def get_create_sql(self):
        """
        Get CREATE TABLE SQL statement
        :return:
        """
        pk = ["ts"] + [f.field_name for f in self.key_fields]
        r = [
            "CREATE TABLE IF NOT EXISTS %s (" % self.table_name,
            ",\n".join("%s %s" % (n, t) for n, t in self.iter_fields()),
            ") ENGINE = MergeTree(date, (%s), 8192)" % ", ".join(pk)
        ]
        return "\n".join(r)

    def ensure_table(self):
        """
        Ensure table is exists
        :return: True, if table has been changed
        """
        from noc.core.clickhouse.connect import connection

        changed = False
        ch = connection()
        if not ch.has_table(self.table_name):
            # Create new table
            ch.execute(post=self.get_create_sql())
            changed = True
        else:
            # Alter when necessary
            existing = {}
            for name, type in ch.execute(
                """
                SELECT name, type
                FROM system.columns
                WHERE
                  database=%s
                  AND table=%s
                """,
                [ch.DB, self.table_name]
            ):
                existing[name] = type
            after = None
            for f, t in self.iter_fields():
                if f not in existing:
                    ch.execute(
                        post="ALTER TABLE %s ADD COLUMN %s %s AFTER %s" % (
                            self.table_name,
                            f, t,
                            after)
                    )
                    changed = True
                after = f
        return changed
