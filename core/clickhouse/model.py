# ----------------------------------------------------------------------
# Clickhouse models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from time import perf_counter

# NOC modules
from noc.core.bi.query import to_sql, escape_field
from noc.config import config
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from .fields import BaseField
from .connect import connection

__all__ = ["Model", "NestedModel"]


class ModelBase(type):
    def __new__(mcs, name, bases, attrs):
        # Initialize class
        cls = type.__new__(mcs, name, bases, attrs)
        # Append _meta
        cls._meta = ModelMeta(
            engine=getattr(cls.Meta, "engine", None),
            db_table=getattr(cls.Meta, "db_table", None),
            description=getattr(cls.Meta, "description", None),
            sample=getattr(cls.Meta, "sample", False),
            tags=getattr(cls.Meta, "tags", None),
            managed=getattr(cls.Meta, "managed", True),
        )
        # Call field.contribute_to_class() for all fields
        for k in attrs:
            if isinstance(attrs[k], BaseField):
                cls._meta.register_field(k, attrs[k])
        # Fill _meta.ordered_fields
        cls._meta.order_fields()
        return cls


class ModelMeta(object):
    def __init__(
        self, engine=None, db_table=None, description=None, sample=False, tags=None, managed=True
    ):
        self.engine = engine
        self.db_table = db_table
        self.description = description
        self.sample = sample
        self.tags = tags
        self.managed = managed
        self.fields = {}  # name -> Field
        self.ordered_fields = []  # fields in order

    def register_field(self, name, field):
        self.fields[name] = field
        field.set_name(name)

    def get_field(self, name):
        return self.fields[name]

    def order_fields(self):
        """
        Fill `ordered_fields`
        :return:
        """
        self.ordered_fields = list(
            sorted(self.fields.values(), key=operator.attrgetter("field_number"))
        )


class Model(object, metaclass=ModelBase):
    class Meta(object):
        engine = None
        db_table = None
        description = None
        sample = False
        tags = None
        managed = True

    def __init__(self, **kwargs):
        self.values = kwargs

    @classmethod
    def _get_db_table(cls):
        return cls._meta.db_table

    @classmethod
    def _get_raw_db_table(cls):
        return f"raw_{cls._meta.db_table}"

    @classmethod
    def _get_distributed_db_table(cls):
        return f"d_{cls._meta.db_table}"

    @classmethod
    def wrap_table(cls, table_name):
        class WrapClass(Model):
            class Meta(object):
                db_table = table_name

        return WrapClass

    @staticmethod
    def quote_name(name):
        """
        Clickhouse-safe field names

        :param name:
        :return:
        """
        if "." in name:
            return "`%s`" % name
        return name

    @classmethod
    def iter_create_sql(cls):
        """
        Yields (field name, db  type) for all model's fields
        :return:
        """
        for field in cls._meta.ordered_fields:
            for fn, db_type in field.iter_create_sql():
                yield fn, db_type

    @classmethod
    def get_create_fields_sql(cls):
        """
        Fields creation statements

        :return: SQL code with field creation statements
        """
        return ",\n".join(
            "%s %s" % (cls.quote_name(name), db_type) for name, db_type in cls.iter_create_sql()
        )

    @classmethod
    def get_create_sql(cls):
        return "\n".join(
            [
                f"CREATE TABLE IF NOT EXISTS {cls._get_raw_db_table()} (",
                cls.get_create_fields_sql(),
                f") ENGINE = {cls._meta.engine.get_create_sql()};",
            ]
        )

    @classmethod
    def cget_create_distributed_sql(cls):
        """
        Get CREATE TABLE for Distributed engine
        :return:
        """
        return (
            f"CREATE TABLE IF NOT EXISTS {cls._get_distributed_db_table()} "
            f"ENGINE = Distributed('{config.clickhouse.cluster}', '{config.clickhouse.db}', '{cls._get_raw_db_table()}')"
        )

    @classmethod
    def get_create_view_sql(cls):
        view = cls._get_db_table()
        if config.clickhouse.cluster:
            src = cls._get_distributed_db_table()
        else:
            src = cls._get_raw_db_table()
        return f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM {src}"

    @classmethod
    def to_json(cls, **kwargs):
        """
        Convert dict of kwargs to JSON-serializable dict

        :param kwargs:
        :return:
        """
        r = {}
        for f in kwargs:
            cls._meta.fields[f].apply_json(r, kwargs[f])
        return r

    @classmethod
    def to_python(cls, row, **kwargs):
        return {
            field.name: field.to_python(row[num])
            for num, field in enumerate(cls._meta.ordered_fields)
        }

    @classmethod
    def ensure_columns(cls, connect, table_name):
        """
        Create necessary table columns

        :param connect: ClickHouse client
        :param table_name: Database table name
        :return: True, if any column has been altered
        """
        c = False  # Changed indicator
        # Get existing columns
        existing = {}
        for name, type in connect.execute(
            """
            SELECT name, type
            FROM system.columns
            WHERE
              database=%s
              AND table=%s
            """,
            [config.clickhouse.db, table_name],
        ):
            existing[name] = type
        # Check
        after = None
        for field_name, db_type in cls.iter_create_sql():
            if field_name in existing:
                # Check types
                name, nested_name = BaseField.nested_path(field_name)
                c_type = cls._meta.fields[name].get_db_type(nested_name)
                if existing[field_name] != c_type:
                    print(
                        "Warning! Type mismatch for column %s: %s <> %s"
                        % (field_name, existing[field_name], c_type)
                    )
                    print(
                        "Set command manually: ALTER TABLE %s MODIFY COLUMN %s %s"
                        % (table_name, field_name, c_type)
                    )

            else:
                connect.execute(
                    post="ALTER TABLE %s ADD COLUMN %s %s AFTER %s"
                    % (table_name, cls.quote_name(field_name), db_type, cls.quote_name(after))
                )
                c = True
            after = field_name
        return c

    @classmethod
    def ensure_table(cls, connect=None):
        """
        Check table is exists
        :param connect:
        :return: True, if table has been altered, False otherwise
        """
        if not cls._meta.managed:
            return False
        changed = False
        ch = connect or connection()
        is_cluster = bool(config.clickhouse.cluster)
        table = cls._get_db_table()
        raw_table = cls._get_raw_db_table()
        dist_table = cls._get_distributed_db_table()
        # Legacy migration
        if ch.has_table(table) and not ch.has_table(raw_table):
            # Legacy scheme, data for non-clustered installations has been written
            # to table itself. Move to raw_*
            ch.rename_table(table, raw_table)
            changed = True
        # Ensure raw_* table
        if ch.has_table(raw_table):
            # raw_* table exists, check columns
            changed |= cls.ensure_columns(ch, raw_table)
        else:
            # Create new table
            ch.execute(post=cls.get_create_sql())
            changed = True
        # For cluster mode check d_* distributed table
        if is_cluster:
            if ch.has_table(dist_table):
                changed |= cls.ensure_columns(ch, dist_table)
            else:
                ch.execute(post=cls.cget_create_distributed_sql())
                changed = True
        # Synchronize view
        if changed or not ch.has_table(table):
            ch.execute(post=cls.get_create_view_sql())
            changed = True
        return changed

    @classmethod
    def transform_query(cls, query, user):
        """
        Transform query, possibly applying access restrictions
        :param query:
        :param user:
        :return: query dict or None if access denied
        """
        if not user or user.is_superuser:
            return query  # No restrictions
        if query["datasource"].startswith("dictionaries."):
            return query  # To dictionaries
        # Get user domains
        domains = UserAccess.get_domains(user)
        # Resolve domains against dict
        mos_bi = [
            int(bi_id)
            for bi_id in ManagedObject.objects.filter(
                administrative_domain__in=domains
            ).values_list("bi_id", flat=True)
        ]
        filter = query.get("filter", {})
        dl = len(mos_bi)
        if not dl:
            return None
        elif dl == 1:
            q = {"$eq": [{"$field": "managed_object"}, mos_bi]}
        else:
            q = {"$in": [{"$field": "managed_object"}, mos_bi]}
        if filter:
            query["filter"] = {"$and": [query["filter"], q]}
        else:
            query["filter"] = q
        return query

    @classmethod
    def query(cls, query, user=None, dry_run=False):
        """
        Execute query and return result
        :param query: dict of
            "fields": list of dicts
                *expr -- field expression
                *alias -- resulting name
                *group -- nth field in GROUP BY expression, starting from 0
                *order -- nth field in ORDER BY expression, starting from 0
                *desc -- sort in descending order, if true
            "filter": expression
            "having": expression
            "limit": N -- limit to N rows
            "offset": N -- skip first N rows
            "sample": 0.0-1.0 -- randomly select rows
            @todo: group by
            @todo: order by
        :param user: User doing query
        :param dry_run: Do not query, only return it.
        :return:
        """
        # Get field expressions
        fields = query.get("fields", [])
        if not fields:
            return None
        transformed_query = cls.transform_query(query, user)
        fields_x = []
        aliases = []
        group_by = {}
        order_by = {}
        for i, f in enumerate(fields):
            if isinstance(f["expr"], str):
                default_alias = f["expr"]
                f["expr"] = {"$field": f["expr"]}
            else:
                default_alias = "f%04d" % i
            alias = f.get("alias", default_alias)
            if not f.get("hide"):
                aliases += [alias]
                fields_x += ["%s AS %s" % (to_sql(f["expr"], cls), escape_field(alias))]
            if "group" in f:
                group_by[int(f["group"])] = alias
            if "order" in f:
                if "desc" in f and f["desc"]:
                    order_by[int(f["order"])] = "%s DESC" % alias
                else:
                    order_by[int(f["order"])] = alias
        if transformed_query is None:
            # Access denied
            r = []
            dt = 0.0
            sql = ["SELECT %s FROM %s WHERE 0 = 1" % (", ".join(fields_x), cls._get_db_table())]
        else:
            # Get where expressions
            filter_x = to_sql(transformed_query.get("filter", {}))
            filter_h = to_sql(transformed_query.get("having", {}))
            # Generate SQL
            sql = ["SELECT "]
            sql += [", ".join(fields_x)]
            sql += ["FROM %s" % cls._get_db_table()]
            sample = query.get("sample")
            if sample:
                sql += ["SAMPLE %s" % float(sample)]
            if filter_x:
                sql += ["WHERE %s" % filter_x]
            # GROUP BY
            if group_by:
                sql += ["GROUP BY %s" % ", ".join(group_by[v] for v in sorted(group_by))]
            # HAVING
            if filter_h:
                sql += ["HAVING %s" % filter_h]
            # ORDER BY
            if order_by:
                sql += ["ORDER BY %s" % ", ".join(order_by[v] for v in sorted(order_by))]
            # LIMIT
            if "limit" in query:
                if "offset" in query:
                    sql += ["LIMIT %d, %d" % (query["offset"], query["limit"])]
                else:
                    sql += ["LIMIT %d" % query["limit"]]
            sql = " ".join(sql)
            # Execute query
            ch = connection()
            t0 = perf_counter()
            if dry_run:
                return sql
            r = ch.execute(sql)
            dt = perf_counter() - t0
        return {"fields": aliases, "result": r, "duration": dt, "sql": sql}

    @classmethod
    def get_pk_name(cls):
        """
        Get primary key's name

        :return: Field name
        """
        return cls._meta.ordered_fields[0].name


class NestedModel(Model):
    @classmethod
    def get_create_sql(cls):
        return cls.get_create_fields_sql()
