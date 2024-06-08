# ---------------------------------------------------------------------
# MetricScope model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Callable, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    EmbeddedDocumentField,
    UUIDField,
    BooleanField,
)
import cachetools

# NOC Modules
from noc.config import config
from noc.core.model.decorator import on_save
from noc.core.prettyjson import to_json
from noc.core.model.decorator import on_delete_check
from noc.main.models.label import Label

id_lock = Lock()
to_path_code = {}
code_lock = Lock()

OLD_PM_SCHEMA_TABLE = "noc_old"


@dataclass
class ExistingColumn:
    name: str
    type: str
    default_kind: Optional[str] = None  # DEFAULT, MATERIALIZED
    default_expression: Optional[str] = None


class KeyField(EmbeddedDocument):
    # Table field name
    field_name = StringField()
    # Model reference, i.e. sa.ManagedObject
    model = StringField()

    def __str__(self):
        return self.field_name

    def to_json(self):
        return {"field_name": self.field_name, "model": self.model}

    @property
    def field_type(self):
        return "UInt64"


class LabelItem(EmbeddedDocument):
    # Wildcard label, noc::<scope>::* is preferable
    label = StringField()
    is_required = BooleanField(default=False)
    is_key_label = BooleanField(default=False)
    # Store data in separate table column `store_field`, if not empty
    # store in `labels` field otherwise
    store_column = StringField()
    # Create separate view column `view_column`, if not empty.
    # Otherwise, create separate view column `store_column` if set.
    # Do not create view column otherwise.
    view_column = StringField()
    # Part of primary key, implies `store_column` if set
    is_primary_key = BooleanField(default=False)
    # Part of order key
    is_order_key = BooleanField(default=False)
    # Legacy path component, for transition period
    # Path position is determined by item position.
    # Do not set for newly created scopes
    is_path = BooleanField(default=False)

    def __str__(self):
        return self.label

    @property
    def field_name(self):
        name = self.label[:-3]  # Strip ::*
        if name.startswith("noc::"):
            return name[5:]
        return name

    @property
    def label_prefix(self):
        return self.label[:-1]  # skip trailing *

    def to_json(self):
        r = {
            "label": self.label,
            "is_required": self.is_required,
            "is_key_label": self.is_key_label,
            "is_primary_key": self.is_primary_key,
            "is_order_key": self.is_order_key,
            "is_path": self.is_path,
        }
        if self.store_column:
            r["store_column"] = self.store_column
        if self.view_column:
            r["view_column"] = self.view_column
        return r


@on_delete_check(check=[("pm.MetricType", "scope"), ("main.MetricStream", "scope")])
@on_save
class MetricScope(Document):
    meta = {
        "collection": "noc.metricscopes",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "pm.metricscopes",
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    # Database table name
    table_name = StringField()
    description = StringField(required=False)
    key_fields = ListField(EmbeddedDocumentField(KeyField))
    labels = ListField(EmbeddedDocumentField(LabelItem))
    enable_timedelta = BooleanField(default=False)

    _id_cache = cachetools.TTLCache(maxsize=30, ttl=300)
    _table_cache = cachetools.TTLCache(maxsize=30, ttl=300)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["MetricScope"]:
        return MetricScope.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_table_cache"), lock=lambda _: id_lock)
    def get_by_table_name(cls, tname) -> Optional["MetricScope"]:
        return MetricScope.objects.filter(table_name=tname).first()

    def on_save(self):
        for label in self.labels:
            Label.ensure_label(
                label.label,
                [],
                description="Auto-created for PM scope",
                is_protected=True,
                expose_metric=True,
            )

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "table_name": self.table_name,
            "description": self.description,
            "key_fields": [kf.to_json() for kf in self.key_fields],
            "labels": [p.to_json() for p in self.labels],
            "enable_timedelta": self.enable_timedelta,
        }
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "table_name",
                "description",
                "key_fields",
                "path",
            ],
        )

    def get_json_path(self) -> str:
        return f"{self.name}.json"

    def iter_metrics_fields(self):
        """
        Yield metric field
        :return:
        """
        from .metrictype import MetricType

        for t in MetricType.objects.filter(scope=self.id).order_by("id"):
            default_value = None
            if config.clickhouse.enable_default_value:
                default_value = getattr(config.clickhouse, f"default_{t.field_type}", None)
            if default_value:
                yield t.field_name, t.field_type, "DEFAULT", default_value or ""
            else:
                yield t.field_name, t.field_type, "", default_value or ""

    def iter_fields(self):
        """
        Yield (field_name, field_type, materialized_expr, default_expr) tuples
        :return:
        """

        yield "date", "Date", "", ""
        yield "ts", "DateTime", "", ""
        yield "metric_type", "String", "", ""
        for f in self.key_fields:
            yield f.field_name, f.field_type, "", ""
        yield "labels", "Array(LowCardinality(String))", "", ""
        if self.enable_timedelta:
            yield "time_delta", "UInt16", "", ""
        for label in self.labels:
            if label.store_column:
                yield label.store_column, "LowCardinality(String)", f"MATERIALIZED splitByString('::', arrayFirst(x -> startsWith(x, '{label.label_prefix}'), labels))[-1]", ""
        yield from self.iter_metrics_fields()

    def get_create_sql(self):
        """
        Get CREATE TABLE SQL statement
        :return:
        """
        # Key Fields
        kf = [f.field_name for f in self.key_fields]
        kf += ["date"]
        pk, ok = kf[:], kf[:]
        for label in self.labels:
            if label.is_order_key or label.is_primary_key:
                # Primary Key must be a prefix of the sorting key
                ok += [f"arrayFirst(x -> startsWith(x, '{label.label_prefix}'), labels)"]
            if label.is_primary_key:
                pk += [f"arrayFirst(x -> startsWith(x, '{label.label_prefix}'), labels)"]
        r = [
            "CREATE TABLE IF NOT EXISTS %s (" % self._get_raw_db_table(),
            ",\n".join(
                f"  {n} {t} {me} {'DEFAULT %s' % de if de else ''}"
                for n, t, me, de in self.iter_fields()
            ),
            f") ENGINE = MergeTree() ORDER BY ({', '.join(ok)})\n",
            f"PARTITION BY toYYYYMM(date) PRIMARY KEY ({', '.join(pk)})",
        ]
        return "\n".join(r)

    def get_create_distributed_sql(self):
        """
        Get CREATE TABLE for Distributed engine
        :return:
        """
        return (
            "CREATE TABLE IF NOT EXISTS %s "
            "AS %s "
            "ENGINE = Distributed(%s, %s, %s)"
            % (
                self._get_distributed_db_table(),
                self._get_raw_db_table(),
                config.clickhouse.cluster,
                config.clickhouse.db,
                self._get_raw_db_table(),
            )
        )

    def get_create_view_sql(self):
        view = self._get_db_table()
        if config.clickhouse.cluster:
            src = self._get_distributed_db_table()
        else:
            src = self._get_raw_db_table()
        # path emulation
        v_path = ""
        path = [label.label_prefix for label in self.labels if label.is_path]
        if path:
            l_exp = ", ".join(
                f"splitByString('::', arrayFirst(x -> startsWith(x, '{pn}'), labels))[-1]"
                for pn in path
            )
            v_path = f"[{l_exp}] AS path, "
        # view columns
        vc_expr = ""
        view_columns = []
        for label in self.labels:
            if label.view_column and label.store_column:
                view_columns += [f"{label.store_column} AS {label.view_column}"]
            elif label.store_column:
                view_columns += [f"{label.store_column}"]
            elif label.view_column:
                view_columns += [
                    f"splitByString('::', arrayFirst(x -> startsWith(x, '{label.label_prefix}'), labels))[-1] AS {label.view_column} "
                ]
        if view_columns:
            vc_expr = ", ".join(view_columns)
            vc_expr += ", "
        f_expr = ""
        if config.clickhouse.enable_default_value:
            # field != default_value
            r = ["date", "ts"]
            if view_columns:
                r += ["labels"]
            for f in self.key_fields:
                r += [f"{f.field_name}"]
            for n, t, me, de in self.iter_metrics_fields():
                r += [f"nullIf({n}, {de}) AS {n}"]
            f_expr = ",".join(r)
        return (
            f"CREATE OR REPLACE VIEW {view} AS SELECT {v_path}{vc_expr}{f_expr or '*'} FROM {src}"
        )

    def _get_db_table(self):
        return self.table_name

    def _get_raw_db_table(self):
        return f"raw_{self.table_name}"

    def _get_distributed_db_table(self):
        return f"d_{self.table_name}"

    def ensure_table(self, connect=None):
        """
        Ensure table is exists
        :return: True, if table has been changed
        """
        from noc.core.clickhouse.connect import connection

        def ensure_column(table_name, column):
            """
            If path not exists on column - new schema
            :param table_name:
            :return:
            """
            return bool(
                ch.execute(
                    """
                SELECT 1
                FROM system.columns
                WHERE
                  database=%s
                  AND table=%s
                  AND name=%s
                """,
                    [config.clickhouse.db, table_name, column],
                )
            )

        def ensure_columns(table_name):
            c = False
            # Alter when necessary
            existing = {}
            for name, c_type, default_expression, default_kind in ch.execute(
                """
                SELECT name, type, default_expression, default_kind
                FROM system.columns
                WHERE
                  database=%s
                  AND table=%s
                """,
                [config.clickhouse.db, table_name],
            ):
                existing[name]: Dict[str, ExistingColumn] = ExistingColumn(
                    name,
                    c_type,
                    default_kind,
                    str(default_expression),
                )
            after = None
            for f, t, me, de in self.iter_fields():
                if f not in existing:
                    ch.execute(
                        post=f"ALTER TABLE {table_name} ADD COLUMN {f} {t} {me} {de} AFTER {after}"
                    )
                    c = True
                after = f
                if f in existing and existing[f].type != t:
                    print(f"Warning! Type mismatch for column {f}: {existing[f]} <> {t}")
                    # print(f"Set command manually: ALTER TABLE {table_name} MODIFY COLUMN {f} {t}")
                    ch.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {f} {t}")
            # Check default value
            for f, t, me, de in self.iter_metrics_fields():
                if f in existing and (existing[f].default_expression or "") != str(de).strip(
                    "0"
                ):  # Strip for float value xxx.
                    if de:
                        ch.execute(post=f"ALTER TABLE {table_name} MODIFY COLUMN {f} DEFAULT {de}")
                    else:
                        ch.execute(
                            post=f"ALTER TABLE {table_name} MODIFY COLUMN {f} REMOVE DEFAULT"
                        )
                    c = True
            return c

        changed = False
        ch = connect or connection(read_only=False)
        is_cluster = bool(config.clickhouse.cluster)
        table = self._get_db_table()
        raw_table = self._get_raw_db_table()
        dist_table = self._get_distributed_db_table()
        # Legacy migration
        if ch.has_table(table) and not ch.has_table(raw_table):
            # Legacy scheme, data for non-clustered installations has been written
            # to table itself. Move to raw_*
            ch.rename_table(table, raw_table)
            changed = True
        # Old schema
        if ch.has_table(raw_table) and not ensure_column(raw_table, "labels"):
            # Old schema, data table will be move to old_noc db for save data.
            ch.ensure_db(OLD_PM_SCHEMA_TABLE)
            ch.rename_table(raw_table, f"{OLD_PM_SCHEMA_TABLE}.{raw_table}")
        # Ensure raw_* table
        if ch.has_table(raw_table):
            # raw_* table exists, check columns
            changed |= ensure_columns(raw_table)
        else:
            # Create new table
            ch.execute(post=self.get_create_sql())
            changed = True
        # For cluster mode check d_* distributed table
        if is_cluster:
            if ch.has_table(dist_table):
                changed |= ensure_columns(dist_table)
            else:
                ch.execute(post=self.get_create_distributed_sql())
                changed = True
        # Synchronize view
        ch.execute(post=self.get_create_view_sql())
        return changed

    def _get_to_path_code(self) -> str:
        """
        Generate to_path() body
        :return:
        """
        p_labels = [(label.label, label.is_required) for label in self.labels if label.is_path]
        r = ["def thunk(labels):"]
        if not p_labels:
            # No path
            r += ["    return []"]
            return "\n".join(r)
        r += [
            "    pc = {}",
            "    max_p = -1",
            "    for label in labels:",
            f"        if len(pc) >= {len(p_labels)}:",
            "            continue",
        ]
        for pn, (ln, is_required) in enumerate(p_labels):
            prefix = ln[:-1]  # Strip trailing `*`
            p_len = len(prefix)
            r += [
                f'        if label.startswith("{prefix}"):',
                f"            pc[{pn}] = label[{p_len}:]",
                f"            max_p = max(max_p, {pn})",
                "            continue",
            ]
        r += [
            "    if not pc:",
            "        return []",
            '    return [pc.get(i) or "" for i in range(max_p + 1)]',
        ]
        return "\n".join(r)

    def _get_to_path(self) -> Callable[[List[str]], List[str]]:
        """
        Generate label -> path function for scope
        :return:
        """
        fn = to_path_code.get(self.name)
        if not fn:
            with code_lock:
                fn = to_path_code.get(self.name)
                if fn:
                    return fn
                # Compile
                code = self._get_to_path_code()
                eval(compile(code, "<string>", "exec"))
                fn = locals()["thunk"]
                to_path_code[self.name] = fn
        return fn

    def to_path(self, labels: List[str]) -> List[str]:
        return self._get_to_path()(labels)
