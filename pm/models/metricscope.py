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
from noc.config import config
from noc.lib.prettyjson import to_json
from noc.core.model.decorator import on_delete_check

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
            "is_required": bool(self.is_required)
        }
        if self.default_value:
            v["default_value"] = self.default_value
        return v


@on_delete_check(check=[
    ("pm.MetricType", "scope")
])
class MetricScope(Document):
    meta = {
        "collection": "noc.metricscopes",
        "strict": False,
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
            "key_fields": [kf.to_json() for kf in self.key_fields],
            "path": [p.to_json() for p in self.path]
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
        pk = [f.field_name for f in self.key_fields]
        if self.path:
            pk += ["path"]
        pk += ["ts"]
        r = [
            "CREATE TABLE IF NOT EXISTS %s (" % self._get_raw_db_table(),
            ",\n".join("  %s %s" % (n, t) for n, t in self.iter_fields()),
            ") ENGINE = MergeTree(date, (%s), 8192)" % ", ".join(pk)
        ]
        return "\n".join(r)

    def get_create_distributed_sql(self):
        """
        Get CREATE TABLE for Distributed engine
        :return:
        """
        return "CREATE TABLE IF NOT EXISTS %s " \
               "AS %s " \
               "ENGINE = Distributed(%s, %s, %s)" % (
                   self.table_name,
                   self._get_raw_db_table(),
                   config.clickhouse.cluster,
                   config.clickhouse.db, self._get_raw_db_table()
               )

    def _get_raw_db_table(self):
        if config.clickhouse.cluster:
            return "raw_%s" % self.table_name
        else:
            return self.table_name

    def ensure_table(self, connect=None):
        """
        Ensure table is exists
        :return: True, if table has been changed
        """
        from noc.core.clickhouse.connect import connection

        def ensure_columns(table_name):
            c = False
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
                [config.clickhouse.db, table_name]
            ):
                existing[name] = type
            after = None
            for f, t in self.iter_fields():
                if f not in existing:
                    ch.execute(
                        post="ALTER TABLE %s ADD COLUMN %s %s AFTER %s" % (
                            table_name,
                            f, t,
                            after)
                    )
                    c = True
                after = f
            return c

        changed = False
        ch = connect or connection(read_only=False)
        if not ch.has_table(self._get_raw_db_table()):
            # Create new table
            ch.execute(post=self.get_create_sql())
            changed = True
        else:
            changed |= ensure_columns(self._get_raw_db_table())
        # Check for distributed table
        if config.clickhouse.cluster:
            if not ch.has_table(self.table_name):
                ch.execute(post=self.get_create_distributed_sql())
                changed = True
            else:
                changed |= ensure_columns(self.table_name)
        return changed
