# ----------------------------------------------------------------------
# Clickhouse models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import string
from random import choices
from typing import List
from time import perf_counter

# NOC modules
from noc.config import config
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from .fields import BaseField, MaterializedField, AggregatedField
from .engines import ReplacingMergeTree, AggregatingMergeTree
from .connect import ClickhouseClient, connection

__all__ = ["Model", "NestedModel", "DictionaryModel", "ViewModel"]

OLD_PM_SCHEMA_TABLE = "noc_old"


class ModelBase(type):
    def __new__(mcs, name, bases, attrs):
        # Initialize class
        cls = type.__new__(mcs, name, bases, attrs)
        # Append _meta
        cls._meta = ModelMeta(
            engine=getattr(cls.Meta, "engine", None),
            db_table=getattr(cls.Meta, "db_table", None),
            description=getattr(cls.Meta, "description", None),
            # Sample key
            sample=getattr(cls.Meta, "sample", False),
            tags=getattr(cls.Meta, "tags", None),
            # Run migrate for model
            run_migrate=getattr(cls.Meta, "run_migrate", True),
            # Local (non-distributed) table
            is_local=getattr(cls.Meta, "is_local", False),
            view_table_source=getattr(cls.Meta, "view_table_source", None),
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
        self,
        engine=None,
        db_table=None,
        description=None,
        sample=False,
        tags=None,
        # Run migrate for model
        run_migrate=True,
        is_local=False,  # Local table, do not create distributed
        view_table_source=None,
    ):
        self.engine = engine
        self.db_table = db_table
        self.description = description
        self.sample = sample
        self.tags = tags
        self.run_migrate = run_migrate
        self.view_table_source = view_table_source
        self.is_local = is_local
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
    def get_materialized_columns(cls) -> List[str]:
        r = []
        for field in cls._meta.ordered_fields:
            if isinstance(field, MaterializedField):
                r.append(field.name)
        return r

    @classmethod
    def get_create_fields_sql(cls):
        """
        Fields creation statements

        :return: SQL code with field creation statements
        """
        return ",\n".join(
            f"{cls.quote_name(name)} {db_type}" for name, db_type in cls.iter_create_sql()
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
            f"CREATE TABLE IF NOT EXISTS {cls._get_distributed_db_table()} AS {cls._get_raw_db_table()} "
            f"ENGINE = Distributed('{config.clickhouse.cluster}', '{config.clickhouse.db}', '{cls._get_raw_db_table()}')"
        )

    @classmethod
    def get_create_view_sql(cls):
        view = cls._get_db_table()
        if config.clickhouse.cluster:
            src = cls._get_distributed_db_table()
        else:
            src = cls._get_raw_db_table()
        q = ["*"] + cls.get_materialized_columns()
        return f"CREATE OR REPLACE VIEW {view} AS SELECT {', '.join(q)} FROM {src}"

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
    def ensure_columns(cls, connect: "ClickhouseClient", table_name: str) -> bool:
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
            f"""
            SELECT name, type
            FROM system.columns
            WHERE
              database='{config.clickhouse.db}'
              AND table='{table_name}'
            """,
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
                        f"[{table_name}|{field_name}] Warning! Type mismatch: "
                        f"{existing[field_name]} <> {c_type}"
                    )
                    print(
                        f"Set command manually: "
                        f"ALTER TABLE {table_name} MODIFY COLUMN {field_name} {c_type}"
                    )

            else:
                print(f"[{table_name}|{field_name}] Alter column")
                query = (
                    f"ALTER TABLE `{table_name}` ADD COLUMN {cls.quote_name(field_name)} {db_type}"
                )
                if after:
                    # None if add before first field
                    query += f" AFTER {cls.quote_name(after)}"
                else:
                    query += " FIRST"
                connect.execute(post=query)
                c = True
            after = field_name
        return c

    @classmethod
    def ensure_schema(cls, connect=None) -> bool:
        return False

    @classmethod
    def check_old_schema(cls, connect: "ClickhouseClient", table_name: str) -> bool:
        """
        Ensure create table Syntax. False for old Syntax, True for New
        :param connect:
        :param table_name:
        :return:
        """
        r = connect.execute(
            f"""
            SELECT engine_full
            FROM system.tables
            WHERE
              database='{config.clickhouse.db}'
              AND name='{table_name}'
              AND engine = 'MergeTree'
              AND (engine_full NOT LIKE 'MergeTree()%' AND engine_full NOT LIKE 'MergeTree %')
            """
        )
        return not bool(r)

    @classmethod
    def ensure_table(cls, connect=None) -> bool:
        """
        Check table is exists
        :param connect:
        :return: True, if table has been altered, False otherwise
        """
        if not cls._meta.run_migrate:
            return False
        changed = False
        ch: "ClickhouseClient" = connect or connection()
        is_cluster = bool(config.clickhouse.cluster)
        table = cls._get_db_table()
        raw_table = cls._get_raw_db_table()
        dist_table = cls._get_distributed_db_table()
        # Legacy migration
        if ch.has_table(table) and not ch.has_table(raw_table):
            # Legacy scheme, data for non-clustered installations has been written
            # to table itself. Move to raw_*
            print(f"[{table}] Legacy migration. Rename {table} -> {raw_table}")
            ch.rename_table(table, raw_table)
            changed = True
        # Old schema
        if ch.has_table(raw_table) and not cls.check_old_schema(ch, raw_table):
            # Old schema, data table will be move to old_noc db for save data.
            print(f"[{table}] Old Schema Move Data to {OLD_PM_SCHEMA_TABLE}.{raw_table}")
            ch.ensure_db(OLD_PM_SCHEMA_TABLE)
            old_table = f"{OLD_PM_SCHEMA_TABLE}.{raw_table}"
            if ch.has_table(f"{OLD_PM_SCHEMA_TABLE}.{raw_table}"):
                old_table = f"{OLD_PM_SCHEMA_TABLE}.{raw_table}_{''.join(choices(string.ascii_letters, k=4))}"
            ch.rename_table(raw_table, old_table)
        # Ensure raw_* table
        if ch.has_table(raw_table):
            # raw_* table exists, check columns
            print(f"[{table}] Check columns")
            changed |= cls.ensure_columns(ch, raw_table)
        else:
            # Create new table
            print(f"[{table}] Create new table")
            ch.execute(post=cls.get_create_sql())
            changed = True
        # For cluster mode check d_* distributed table
        if is_cluster and not cls._meta.is_local:
            print(f"[{table}] Check distributed table")
            if ch.has_table(dist_table):
                changed |= cls.ensure_columns(ch, dist_table)
            else:
                ch.execute(post=cls.cget_create_distributed_sql())
                changed = True
        if not ch.has_table(table, is_view=True):
            print(f"[{table}] Synchronize view")
            ch.execute(post=cls.get_create_view_sql())
            changed = True
        return changed

    @classmethod
    def ensure_views(cls, connect=None, changed: bool = True) -> bool:
        # Synchronize view
        ch: "ClickhouseClient" = connect or connection()
        table = cls._get_db_table()
        if changed or not ch.has_table(table, is_view=True):
            print(f"[{table}] Synchronize view")
            ch.execute(post=cls.get_create_view_sql())
            return True
        return False

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
        from noc.core.bi.query import to_sql, escape_field

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


class DictionaryBase(ModelBase):
    def __new__(mcs, name, bases, attrs):
        from .fields import DateTimeField, UInt64Field

        # Initialize class
        cls = type.__new__(mcs, name, bases, attrs)
        # Append _meta
        cls._meta = DictionaryMeta(
            name=getattr(cls.Meta, "name"),
            engine=getattr(
                cls.Meta,
                "engine",
                ReplacingMergeTree(None, order_by=getattr(cls.Meta, "primary_key", ("bi_id",))),
            ),
            source_model=getattr(cls.Meta, "source_model", None),
            db_table=f'dict_{getattr(cls.Meta, "name", None)}',
            primary_key=getattr(cls.Meta, "primary_key", ("bi_id",)),
            incremental_update=getattr(cls.Meta, "incremental_update", False),
            description=getattr(cls.Meta, "description", None),
            run_migrate=getattr(cls.Meta, "run_migrate", True),
            is_local=getattr(cls.Meta, "is_local", True),
            view_table_source=getattr(cls.Meta, "view_table_source", None),
            # For Dictionary table
            layout=getattr(cls.Meta, "layout", "hashed"),
            lifetime_min=getattr(cls.Meta, "lifetime_min", 360),
            lifetime_max=getattr(cls.Meta, "lifetime_max", 360),
        )
        # Call field.contribute_to_class() for all fields
        cls._meta.register_field("ts", DateTimeField())
        cls._meta.register_field("bi_id", UInt64Field())
        for k in attrs:
            if isinstance(attrs[k], BaseField):
                cls._meta.register_field(k, attrs[k])
        # Fill _meta.ordered_fields
        cls._meta.order_fields()
        return cls


class DictionaryMeta(object):
    def __init__(
        self,
        name=None,
        engine=None,
        source_model=None,
        primary_key=("bi_id",),
        incremental_update=False,
        db_table=None,
        description=None,
        run_migrate=True,
        is_local=False,  # Local table, do not create distributed
        view_table_source=None,
        layout=None,
        lifetime_min=360,
        lifetime_max=360,
    ):
        self.name = name  # Dictionary name
        self.engine = engine
        self.source_model = source_model
        self.primary_key = primary_key
        self.incremental_update = incremental_update
        self.db_table = db_table or name
        self.description = description
        self.view_table_source = view_table_source
        self.run_migrate = run_migrate
        self.is_local = is_local
        self.layout = layout
        self.lifetime_min = lifetime_min
        self.lifetime_max = lifetime_max
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


class DictionaryModel(Model, metaclass=DictionaryBase):
    class Meta(object):
        name = None
        engine = None
        source_model = None
        description = None

    _collection = None
    _seq = None

    @classmethod
    def _getdictionary_table(cls):
        return f"{config.clickhouse.db_dictionaries}.{cls._meta.name}"

    @classmethod
    def _get_layout(cls):
        return f"{cls._meta.layout.upper()}()"

    @classmethod
    def get_config(cls):
        """
        Generate XML config
        :return:
        """
        x = [
            "<dictionaries>",
            "    <comment>Generated by NOC, do not change manually</comment>",
            "    <dictionary>",
            "        <name>%s</name>" % cls._meta.name,
            "        <lifetime>",
            "            <min>%s</min>" % cls._meta.lifetime_min,
            "            <max>%s</max>" % cls._meta.lifetime_max,
            "        </lifetime>",
            "        <layout>",
            "            <%s />" % cls._meta.layout,
            "        </layout>",
            "        <source>",
            "            <http>",
            '                <url>http://{{ range $index, $element := service "datasource~_agent"}}{{if eq $index 0}}{{.Address}}:{{.Port}}{{end}}{{else}}127.0.0.1:65535{{ end }}/api_datasource/ch_%s.tsv</url>'
            % cls._meta.name,
            "                <format>TabSeparated</format>",
            "            </http>",
            "        </source>",
            "        <structure>",
            "             <id>",
            "                 <name>bi_id</name>",
            "             </id>",
        ]
        for field in cls._meta.ordered_fields:
            if field.name in cls._meta.primary_key or field.name == "ts":
                continue
            hier = getattr(field, "is_self_reference", False)
            x += [
                "             <attribute>",
                "                 <name>%s</name>" % field.name,
                "                 <type>%s</type>" % field.get_db_type(),
                "                 <null_value>Unknown</null_value>",
                "                 <hierarchical>%s</hierarchical>" % ("true" if hier else "false"),
                "             </attribute>",
            ]
        x += ["        </structure>", "    </dictionary>", "</dictionaries>"]
        return "\n".join(x)

    @classmethod
    def get_field_type(cls, name):
        """
        Returns field type

        :param name:
        :return:
        """
        return cls._meta.fields[name].get_db_type()

    @classmethod
    def get_pk_name(cls):
        """
        Get primary key's name

        :return: Field name
        """
        if "name" in cls._meta.fields:
            return "name"
        return cls._meta.ordered_fields[0].name

    @classmethod
    def get_create_view_sql(cls):
        """
        CREATE VIEW noc.v_mo_dict1 (`bi_id` UInt64, `name` String, `address` String)
         AS  select argMax(managed_object, ts) as bi_id,
          argMax(name,ts) as name ,
           argMax(ip,ts) as address
            from mo_datastream group by managed_object;
        """
        r = []
        for field in cls._meta.ordered_fields:
            if field.name in cls._meta.primary_key:
                r += [f"{cls.quote_name(field.name)} AS {field.name}"]
                continue
            elif field.name == "ts" and cls._meta.incremental_update:
                r += [f"argMax({cls.quote_name(field.name)}, ts) AS last_changed"]
                continue
            elif field.name == "ts":
                continue
            r += [f"argMax({cls.quote_name(field.name)}, ts) AS {field.name}"]
        r = ",\n".join(r)
        view = cls._get_db_table()
        src = cls._get_raw_db_table()
        return f'CREATE OR REPLACE VIEW {view} AS SELECT {r} FROM {src} GROUP BY {", ".join(cls._meta.primary_key)}'

    @classmethod
    def iter_create_sql(cls, is_dictionary=False):
        """
        Yields (field name, db  type) for all model's fields
        :return:
        """
        for field in cls._meta.ordered_fields:
            for fn, db_type in field.iter_create_sql():
                if is_dictionary and getattr(field, "is_self_reference", None):
                    db_type = f"{db_type} HIERARCHICAL"
                elif is_dictionary and cls._meta.incremental_update and fn == "ts":
                    fn = "last_changed"
                yield fn, db_type

    @classmethod
    def get_create_dictionary_sql(cls):
        """
        CREATE OR REPLACE DICTIONARY default.mo_dic1 (     bi_id UInt64,     name String,     ip String )
         PRIMARY KEY bi_id
          SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER 'noc' PASSWORD '' DB 'noc' TABLE 'v_mo_dict1' WHERE ''))
           LIFETIME(MIN 300 MAX 360) LAYOUT(HASHED()) ;
        """
        r = []
        for name, db_type in cls.iter_create_sql(is_dictionary=True):
            if name == "ts":
                continue
            r += [f"{cls.quote_name(name)} {db_type}"]
        update_field = ""
        if cls._meta.incremental_update:
            update_field = "UPDATE_FIELD 'last_changed' UPDATE_LAG 15"
        return (
            f'CREATE DICTIONARY IF NOT EXISTS {cls._getdictionary_table()} ({", ".join(r)}) '
            f'PRIMARY KEY {", ".join(cls._meta.primary_key)} '
            f"SOURCE(CLICKHOUSE(HOST 'localhost' PORT 9000 USER '{config.clickhouse.ro_user}' "
            f"PASSWORD '{config.clickhouse.ro_password}' DB '{config.clickhouse.db}' "
            f"TABLE '{cls._get_db_table()}' WHERE '' {update_field})) "
            f"LIFETIME(MIN {cls._meta.lifetime_min} MAX {cls._meta.lifetime_max}) "
            f"LAYOUT({cls._get_layout()})"
        )

    @classmethod
    def detach_dictionary(cls, connect=None):
        ch = connect or connection()
        ch.execute(post=f" DETACH DICTIONARY IF EXISTS {cls._getdictionary_table()}")
        return True

    @classmethod
    def drop_dictionary(cls, connect=None):
        ch = connect or connection()
        ch.execute(post=f" DROP DICTIONARY IF EXISTS {cls._getdictionary_table()}")
        return True

    @classmethod
    def ensure_dictionary(cls, connect=None) -> bool:
        """
        Check dictionary is exists
        :param connect:
        :return: True, if table has been altered, False otherwise
        """
        # changed = False
        ch = connect or connection()
        return bool(ch.execute(post=cls.get_create_dictionary_sql()))

    @classmethod
    def dump(cls, out):
        # @todo: !!!
        raise NotImplementedError()

    @classmethod
    def extract(cls, item):
        raise NotImplementedError


class ViewModel(Model, metaclass=ModelBase):
    # ViewModel

    @classmethod
    def is_aggregate(cls) -> bool:
        return isinstance(cls._meta.engine, AggregatingMergeTree)

    @classmethod
    def ensure_schema(cls, connect=None) -> bool:
        """
        # how to convert MV implicit storage .inner (without TO) to explicit storage (with TO)
        1. stop ingestion
        2. detach table MVX
        3. rename table `.inner.MVX` to MVX_store;
        4. create table `.inner.MVX` as MVX_store engine=TinyLog;
        5. attach table MVX
        6. drop table MVX
        7. rename table MVX_store to MVX
        8. create materialized view MVX_mv to MVX as select ....
        9. start ingestion
        :param connect:
        :return:
        """
        if not cls.is_aggregate():
            return False
        ch = connect or connection()
        inner_table_name = f".inner.{cls._get_raw_db_table()}"
        tmp_inner_table_name = f"{cls._get_raw_db_table()}_store"
        if not ch.has_table(inner_table_name):
            return False
        print(f"[{cls._get_raw_db_table()}] Migrate old materialized view. For use TO statement")
        # Drop view
        ch.execute(post=f"DROP VIEW IF EXISTS {cls._get_db_table()}")
        # Detach MV
        cls.detach_view(connect=ch)
        ch.rename_table(inner_table_name, tmp_inner_table_name)
        ch.execute(f"CREATE TABLE `{inner_table_name}` AS {tmp_inner_table_name} ENGINE=TinyLog")
        ch.execute(post=f"ATTACH TABLE {cls._get_raw_db_table()}")
        cls.drop_view(connect=ch)
        # Rename table
        ch.rename_table(tmp_inner_table_name, cls._get_raw_db_table())
        return True

    @classmethod
    def get_create_view_sql(cls):
        r = []
        group_by = []
        for field in cls._meta.ordered_fields:
            if isinstance(field, AggregatedField):
                r += [f"{field.get_expression(combinator='Merge')} AS {cls.quote_name(field.name)}"]
            else:
                r += [f"{cls.quote_name(field.name)} "]
                group_by += [cls.quote_name(field.name)]
        r = [",\n".join(r)]
        if config.clickhouse.cluster:
            r += [f"FROM {cls._get_distributed_db_table()} "]
        else:
            r += [f"FROM {cls._get_raw_db_table()} "]
        r += [f'GROUP BY {",".join(group_by)} ']
        return f'CREATE OR REPLACE VIEW {cls._get_db_table()} AS SELECT {" ".join(r)}'

    @classmethod
    def get_create_select_sql(cls):
        r = []
        group_by = []
        for field in cls._meta.ordered_fields:
            if isinstance(field, MaterializedField):
                continue
            elif isinstance(field, AggregatedField):
                r += [f"{field.get_expression(combinator='State')} AS {cls.quote_name(field.name)}"]
            else:
                r += [f"{cls.quote_name(field.name)} "]
                group_by += [cls.quote_name(field.name)]
        r = [",\n".join(r)]
        r += [f"FROM {cls.Meta.view_table_source} "]
        r += [f'GROUP BY {",".join(group_by)} ']
        return "\n".join(r)

    @classmethod
    def detach_view(cls, connect=None):
        ch = connect or connection()
        ch.execute(post=f" DETACH VIEW IF EXISTS {cls._get_raw_db_table()}")
        return True

    @classmethod
    def drop_view(cls, connect=None):
        ch = connect or connection()
        ch.execute(post=f" DROP VIEW IF EXISTS {cls._get_raw_db_table()}")
        return True

    @classmethod
    def ensure_mv_trigger_view(cls, connect=None):
        mv_name = f"mv_{cls._get_raw_db_table()}"
        connect.execute(post=f" DROP VIEW IF EXISTS {mv_name}")
        connect.execute(
            post="\n".join(
                [
                    f"CREATE MATERIALIZED VIEW IF NOT EXISTS {mv_name} "
                    f"TO {cls._get_raw_db_table()} "
                    f"AS SELECT {cls.get_create_select_sql()}",
                ]
            )
        )
        return True

    @classmethod
    def ensure_views(cls, connect=None, changed: bool = True) -> bool:
        # Synchronize view
        ch: "ClickhouseClient" = connect or connection()
        table = cls._get_db_table()
        if changed or not ch.has_table(table, is_view=True):
            print(f"[{table}] Synchronize view")
            cls.ensure_mv_trigger_view(ch)
            ch.execute(post=cls.get_create_view_sql())
            return True
        return False
