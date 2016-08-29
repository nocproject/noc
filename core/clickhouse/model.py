# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clickhouse models
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from six import with_metaclass
## NOC modules
from fields import BaseField
from noc.core.clickhouse.connect import connection

__all__ = ["Model"]


class ModelBase(type):
    def __new__(mcs, name, bases, attrs):
        cls = type.__new__(mcs, name, bases, attrs)
        cls._fields = {}
        cls._meta = ModelMeta(
            engine=getattr(cls.Meta, "engine", None),
            db_table=getattr(cls.Meta, "db_table", None),
            description=getattr(cls.Meta, "description", None),
            tags=getattr(cls.Meta, "tags", None),
        )
        for k in attrs:
            if isinstance(attrs[k], BaseField):
                cls._fields[k] = attrs[k]
                cls._fields[k].name = k
        cls._fields_order = sorted(
            cls._fields, key=lambda x: cls._fields[x].field_number
        )
        return cls


class ModelMeta(object):
    def __init__(self, engine=None, db_table=None, description=None,
                 tags=None):
        self.engine = engine
        self.db_table = db_table
        self.description = description
        self.tags = tags


class Model(with_metaclass(ModelBase)):
    class Meta:
        engine = None
        db_table = None
        description = None
        tags = None

    def __init__(self, **kwargs):
        self.values = kwargs

    @classmethod
    def get_create_sql(cls):
        r = ["CREATE TABLE IF NOT EXISTS %s (" % cls._meta.db_table]
        r += [",\n".join(cls._fields[f].get_create_sql() for f in cls._fields_order)]
        r += [") ENGINE = %s;" % cls._meta.engine.get_create_sql()]
        return "\n".join(r)

    @classmethod
    def to_tsv(cls, **kwargs):
        return "\t".join(
            cls._fields[f].to_tsv(kwargs[f]) for f in cls._fields_order
        ) + "\n"

    @classmethod
    def ensure_table(cls):
        ch = connection()
        if not ch.has_table(cls._meta.db_table):
            # Create new table
            ch.execute(post=cls.get_create_sql())
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
                [ch.DB, cls._meta.db_table]
            ):
                existing[name] = type
            after = None
            for f in cls._fields_order:
                if f not in existing:
                    ch.execute(post="ALTER TABLE %s ADD COLUMN %s AFTER %s" % (
                        cls._meta.db_table, cls._fields[f].get_create_sql(), after))
                after = f

    @classmethod
    def get_model_class(cls, name):
        """
        Returns model class referred by name
        @todo: Process custom/
        :param name:
        :return:
        """
        m = __import__("noc.core.bi.models.%s" % name, {}, {}, "*")
        for a in dir(m):
            o = getattr(m, a)
            if not hasattr(o, "_meta"):
                continue
            if getattr(o._meta, "db_table", None) == name:
                return o
        return None
