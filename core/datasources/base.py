# ----------------------------------------------------------------------
# DataSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
import operator
import uuid
import orjson
from time import perf_counter
from dataclasses import dataclass
from functools import partial
from collections import defaultdict
from typing import Tuple, Union, Optional, Iterable, List, Dict, AsyncIterable, Set, Any

# Third-party modules
import polars as pl

# NOC modules
from noc.core.diagnostic.types import DiagnosticState
from noc.core.clickhouse.connect import ClickhouseClient, connection
from noc.core.clickhouse.error import ClickhouseError
from noc.core.msgstream.client import MessageStreamClient
from noc.models import get_model
from noc.config import config


@dataclass
class ClickhouseColumn:
    name: str
    type: str
    default_kind: Optional[str] = None  # DEFAULT, MATERIALIZED
    default_expression: Optional[str] = None

    def __hash__(self):
        """"""
        return hash(self.name)


@dataclass
class DSSnapshot:
    """Datasource snapshot"""

    name: str
    report_ts: datetime.datetime
    report_uuid: Optional[uuid.UUID] = None
    job_uuid: Optional[uuid.UUID] = None
    labels: Optional[List[str]] = None


clean_map = {
    "str": lambda x: str(x),
    "int": lambda x: int(x),
    "float": lambda x: float(x),
    "date": lambda x: datetime.date.fromisoformat(x),
    "datetime": lambda x: datetime.datetime.fromisoformat(x),
    "bool": lambda x: bool(x),
}


class FieldType(enum.Enum):
    STRING = pl.Utf8
    INT = pl.Int64
    UINT = pl.UInt32
    UINT64 = pl.UInt64
    INT32 = pl.Int32
    FLOAT = pl.Float32
    BOOL = pl.Boolean
    DATETIME = pl.Datetime
    LIST_STRING = pl.List(pl.Utf8)

    @property
    def clickhouse_db_type(self) -> str:
        """Return clickhouse DB type"""
        match self:
            case self.INT | self.INT32:
                return "Int32"
            case self.UINT:
                return "UInt32"
            case self.UINT64:
                return "UInt64"
            case self.BOOL:
                return "Bool"
            case self.FLOAT:
                return "Float32"
            case self.DATETIME:
                return "DateTime"
            case self.LIST_STRING:
                return "Array(LowCardinality(String))"
        return "String"

    def clean_clickhouse_value(self, value) -> Any:
        """Convert value to clickhouse"""
        return value


caps_dtype_map = {
    "bool": FieldType.BOOL,
    "str": FieldType.STRING,
    "int": FieldType.UINT,
    "float": FieldType.FLOAT,
    "strlist": FieldType.LIST_STRING,
}


@dataclass
class FieldInfo(object):
    """
    Datasource Field description
    """

    name: str  # Name for external interaction
    description: Optional[str] = None
    internal_name: Optional[str] = None  # Name for internal DataSource used
    type: FieldType = FieldType.STRING  # Field type
    is_caps: bool = False  # Capability field
    is_virtual: bool = False  # Virtual Field not sending to output
    is_vector: bool = False  # Multiple column by requested one field
    is_diagnostic_state: Optional[DiagnosticState] = None  # Request Diagnostic State field

    @property
    def clickhouse_column(self) -> ClickhouseColumn:
        """Generate clickhouse column"""
        return ClickhouseColumn(name=self.name, type=self.type.clickhouse_db_type)


@dataclass
class ParamInfo:
    """Datasource Params description"""

    name: str
    type: str  # str, int, float, date, time
    required: bool = False
    allow_multi: bool = False
    resolve_nested: bool = True
    display_label: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    model: Optional[str] = None

    def clean_value(self, value: Union[str, List[str]]):
        if not isinstance(value, list):
            value = [value]
        if self.model and self.resolve_nested and self.allow_multi:
            values = self.clean_nested_model(value)
        elif self.model:
            m = get_model(self.model)
            values = [self.clean_model(m, v) for v in value]
        else:
            values = [self.clean_type(v) for v in value]
        if self.allow_multi:
            return values
        return values[0]

    def clean_type(self, value: str):
        if self.type == "date" and isinstance(value, datetime.date):
            return value
        if self.type == "datetime" and isinstance(value, datetime.datetime):
            return value
        return clean_map[self.type](value)

    def clean_nested_model(self, values: List[Any]) -> List[Any]:
        r = set()
        m = get_model(self.model)
        for v in values:
            v = self.clean_model(m, v)
            r |= set(m.get_nested_ids(v.id))
        return list(r)

    def clean_model(self, model, value: Union[str, Any]) -> Optional[Any]:
        """Convert value to model filter"""
        if not isinstance(value, model):
            value = model.get_by_id(value)
        return value


class BaseDataSource(object):
    """DataSource and fields description"""

    IGNORED_PARAMS = {"administrative_domain", "user"}
    DEFAULT_INTERVAL = 2 * 86400
    ENABLE_CH_MIRROR = False

    name: str
    fields: List[FieldInfo]
    params: Optional[List[ParamInfo]] = None
    row_index: Union[str, Tuple[str, ...]] = "id"

    @classmethod
    def clickhouse_mirror(cls) -> bool:
        """Allowed ClickHouse create table"""
        return cls.ENABLE_CH_MIRROR

    @classmethod
    def join_fields(cls) -> List[str]:
        if not cls.row_index:
            return []
        if cls.row_index and isinstance(cls.row_index, str):
            return [cls.row_index]
        return list(cls.row_index)

    @classmethod
    def iter_ds_fields(cls) -> Iterable[FieldInfo]:
        for f in cls.fields:
            yield f

    @classmethod
    def field_by_name(cls, name: str) -> FieldInfo:
        for f in cls.fields:
            if f.name == name:
                return f

    @classmethod
    def clean_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        r = {}
        if "user" in params or "administrative_domain" in params:
            idx = cls.get_ads_filter(
                params.get("user"),
                params.get("administrative_domain"),
            )
            r["admin_domain_ads"] = idx
        for p in cls.params or []:
            if p.name in cls.IGNORED_PARAMS:
                continue
            if p.name in params:
                v = p.clean_value(params[p.name])
            elif p.default:
                v = p.default
            else:
                continue
            r[p.name] = v
        return r

    @staticmethod
    def get_ads_filter(
        user: Optional[Any] = None,
        administrative_domain: Optional[Union[List[Any], Any]] = None,
    ) -> Optional[List[int]]:
        """
        Build Administrative Domain filter
        """
        from noc.sa.models.useraccess import UserAccess
        from noc.sa.models.administrativedomain import AdministrativeDomain

        ads = set()
        # Normalize administrative domain
        administrative_domain = administrative_domain or []
        if not isinstance(administrative_domain, list):
            administrative_domain = [administrative_domain]
        for ad in administrative_domain:
            if isinstance(ad, AdministrativeDomain):
                ads |= set(AdministrativeDomain.get_nested_ids(ad.id))
            else:
                ads |= set(AdministrativeDomain.get_nested_ids(int(ad)))
        # Normalize user
        if not user or user.is_superuser:
            return list(ads) or None
        user_ads = set(UserAccess.get_domains(user))
        if not ads:
            return list(user_ads)
        ads = ads & user_ads
        return list(ads)

    @classmethod
    def clean_interval(
        cls,
        start: datetime.datetime,
        end: Optional[datetime.datetime] = None,
        period: Optional[int] = None,
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """Clean datetime interval"""
        end = (end or datetime.datetime.now()).replace(microsecond=0)
        start = start or end - datetime.timedelta(seconds=period or cls.DEFAULT_INTERVAL)
        return start, end

    @classmethod
    def query_sync(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pl.DataFrame:
        """
        Sync method for query report data
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """
        from noc.core.ioloop.util import run_sync

        return run_sync(partial(cls.query, fields, *args, **kwargs))

    @classmethod
    def get_columns_dtype(cls, fields: Optional[List[str]] = None):
        """
        Return Column Dtype
        columns=[("col1", pl.Float32), ("col2", pl.Int64)]
        :return:
        """
        c_map = {
            "string": pl.Utf8,
            "str": pl.Utf8,
            "int64": pl.Int64,
            "bool": pl.Boolean,
            "int": pl.Int32,
            "float": pl.Float32,
        }
        r = {}
        for f in cls.iter_ds_fields():
            if fields and f.name not in fields:
                continue
            r[f.name] = c_map[f.type]
        return r

    @classmethod
    def has_field(cls, name) -> bool:
        return any(f.name == name for f in cls.iter_ds_fields())

    @classmethod
    def is_out_field(cls, f: FieldInfo, fields: Optional[Set[str]] = None) -> bool:
        """
        Check field allowed to out
        """
        if f.is_virtual:
            # Virtual Field
            return False
        if not fields:
            # Not filtered field
            return True
        if cls.row_index and f.name == cls.row_index:
            return True
        return f.name in fields

    @classmethod
    def get_series_from_data(cls, data: Dict[str, List[Any]], fields: Optional[Set[str]] = None):
        """Getting dataframe from series columns data"""
        series = []
        for c in cls.iter_ds_fields():
            if len(data[c.name]) and (
                cls.is_out_field(c, fields) or (c.is_vector and c.name in data)
            ):
                try:
                    series.append(pl.Series(c.name, data[c.name], dtype=c.type.value))
                except TypeError:
                    print(f"Type Error on column: {c.name}. Will be skipping")
                except OverflowError:
                    print(f"OverflowError on column: {c.name}. Will be skipping")
                except pl.exceptions.InvalidOperationError:
                    print(f"Invalid Operation Cast on column: {c.name}. Will be skipping")
        return series

    @classmethod
    async def query(
        cls,
        fields: Optional[Iterable[str]] = None,
        mirror_clickhouse: bool = False,
        report_uuid: Optional[uuid.UUID] = None,
        *args,
        **kwargs,
    ) -> pl.DataFrame:
        """
        Method for query report data. Return pandas dataframe.
        Args:
            fields: list fields for filtered on query
            mirror_clickhouse: Send data to clickhouse
            report_uuid: Report UUID bild
            args: arguments for report query
            kwargs:
        """
        r = defaultdict(list)
        started = perf_counter()
        params = cls.clean_params(kwargs)
        async for _, f_name, value in cls.iter_query(fields, *args, **params):
            r[f_name].append(value)
        print(f"Execute query: {perf_counter() - started:.2f} sec.")
        fields = set(fields or [])
        if not r:
            return pl.DataFrame(
                [],
                schema=[
                    (c.name, c.type.value)
                    for c in cls.iter_ds_fields()
                    if cls.is_out_field(c, fields)
                ],
            )
        series = cls.get_series_from_data(r, fields)
        if not mirror_clickhouse:
            return pl.DataFrame(series)
        if not cls.clickhouse_mirror():
            print("Datasource mirroring not supported")
            return pl.DataFrame(series)
        df = pl.DataFrame(series)
        await cls.publish_clickhouse(df, report_uuid=report_uuid)
        return df
        # return pl.DataFrame(r, columns=[(c.name, c.type.value) for c in cls.fields])

    @classmethod
    def get_clickhouse_snapshots(cls, ttl: Optional[datetime.datetime] = None) -> List[DSSnapshot]:
        """Return available snapshots for Datasource"""
        if not cls.clickhouse_mirror():
            return []
        ch: "ClickhouseClient" = connection()
        result = ch.execute(
            f"SELECT distinct(report_ts, report_ds as name, report_uuid, job_uuid, labels) as ds FROM {cls._get_db_table()} FORMAT JSON",
            return_raw=True,
        )
        r = []
        for row in orjson.loads(result)["data"]:
            ts, name, report_uuid, job_uuid, labels = row["ds"]
            report_uuid = (
                uuid.UUID(job_uuid)
                if report_uuid != "00000000-0000-0000-0000-000000000000"
                else None
            )
            job_uuid = (
                uuid.UUID(job_uuid) if job_uuid != "00000000-0000-0000-0000-000000000000" else None
            )
            r.append(
                DSSnapshot(
                    name=name,
                    report_ts=datetime.datetime.fromisoformat(ts),
                    report_uuid=report_uuid,
                    job_uuid=job_uuid,
                    labels=labels,
                )
            )
        return r

    @classmethod
    def get_latest_snapshot(cls, ttl: Optional[int] = None) -> Optional[DSSnapshot]:
        """"""
        snapshots = cls.get_clickhouse_snapshots(ttl)
        if not snapshots:
            return None
        r = sorted(snapshots, key=operator.attrgetter("report_ts"), reverse=True)
        return r[0]

    @classmethod
    def from_clickhouse(cls, report_uuid: Optional[uuid.UUID] = None) -> Optional[pl.DataFrame]:
        """Extract Datasource data from Clickhouse"""
        ch: "ClickhouseClient" = connection()
        snapshot = cls.get_latest_snapshot()
        r = ch.execute(
            f"SELECT * FROM {cls._get_db_table()} WHERE report_ts = %s FORMAT JSONColumns",
            return_raw=True,
            args=[snapshot.report_ts.isoformat()],
        )
        r = orjson.loads(r)
        if not r:
            return None
        series = cls.get_series_from_data(r)
        return pl.DataFrame(series)

    @classmethod
    async def publish_clickhouse(
        cls,
        df: pl.DataFrame,
        report_uuid: Optional[uuid.UUID] = None,
        job_uuid: Optional[uuid.UUID] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        """Send DataFrame to clickhouse"""
        ts = (ts or datetime.datetime.now()).replace(microsecond=0)
        ch_row = {
            "date": ts.date().isoformat(),
            "report_ts": ts.isoformat(sep=" "),
            "job_uuid": None,
            "labels": [],
            "report_ds": cls.name,
        }
        if report_uuid:
            ch_row["report_uuid"] = str(report_uuid)
        data = []
        CHUNK = 200
        n_parts = len(config.clickhouse.cluster_topology.split(","))
        async with MessageStreamClient() as client:
            for row in df.iter_rows(named=True):
                row |= ch_row
                data.append(orjson.dumps(row))
                if len(data) < CHUNK:
                    continue
                for part in range(n_parts):
                    await client.publish(
                        b"\n".join(data),
                        stream=f"ch.{cls._get_db_table()}",
                        partition=part,
                    )
                data = []
        if data:
            for part in range(n_parts):
                await client.publish(
                    b"\n".join(data),
                    stream=f"ch.{cls._get_db_table()}",
                    partition=part,
                )

    @classmethod
    async def iter_row(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Dict[str, str]]:
        """
        Iterate data as row
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """
        r = {}
        c_row = 1
        params = cls.clean_params(kwargs)
        async for row_num, f_name, value in cls.iter_query(fields, *args, **params):
            if c_row != row_num:
                yield r
                c_row = row_num
                r = {}
            r[f_name] = cls.clean_row_value(value)

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        """
        Method for query report data. Iterate over field data
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """

    @classmethod
    def clean_row_value(cls, value):
        return value

    @classmethod
    def iter_create_sql(cls) -> Iterable[ClickhouseColumn]:
        """Yield (field_name, field_type, materialized_expr, default_expr) tuples"""

        yield ClickhouseColumn(name="date", type="Date")
        yield ClickhouseColumn(name="report_ts", type="DateTime")
        yield ClickhouseColumn(name="report_ds", type="String")
        yield ClickhouseColumn(name="report_uuid", type="UUID")
        yield ClickhouseColumn(name="job_uuid", type="UUID")
        yield ClickhouseColumn(name="labels", type="Array(LowCardinality(String))")
        for f in cls.iter_ds_fields():
            yield f.clickhouse_column

    @classmethod
    def get_create_sql(cls) -> str:
        """
        Get CREATE TABLE SQL statement
        """
        # Key Fields
        r = [
            "CREATE TABLE IF NOT EXISTS %s (" % cls._get_raw_db_table(),
            ",\n".join(
                f"  {c.name} {c.type} {c.default_kind or ''} {'DEFAULT %s' % c.default_expression if c.default_expression else ''}"
                for c in cls.iter_create_sql()
            ),
            ") ENGINE = MergeTree() ORDER BY (date, job_uuid)\n",
            "PARTITION BY toYYYYMM(date) PRIMARY KEY (date, job_uuid)",
        ]
        return "\n".join(r)

    @classmethod
    def get_create_distributed_sql(cls):
        """
        Get CREATE TABLE for Distributed engine
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
        q = ["*"]
        return f"CREATE OR REPLACE VIEW {view} AS SELECT {', '.join(q)} FROM {src}"

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

    @staticmethod
    def quote_name(name):
        """Clickhouse-safe field names"""
        if "." in name:
            return "`%s`" % name
        return name

    @classmethod
    def _get_db_table(cls):
        return f"report_{cls.name}"

    @classmethod
    def _get_raw_db_table(cls):
        return f"raw_report_{cls.name}"

    @classmethod
    def _get_distributed_db_table(cls):
        return f"d_report_{cls.name}"

    @classmethod
    def ensure_columns(cls, connect: "ClickhouseClient", table_name: str) -> bool:
        """
        Create necessary table columns
        Args:
            connect: ClickHouse client
            table_name: Database table name
        Return:
            True, if any column has been altered
        """
        c = False  # Changed indicator
        # Get existing columns
        existing = {}
        for name, c_type in connect.execute(
            f"""
            SELECT name, type
            FROM system.columns
            WHERE
              database='{config.clickhouse.db}'
              AND table='{table_name}'
            """,
        ):
            existing[name] = c_type
        # Check
        after = None
        for field in cls.iter_create_sql():
            if field.name in existing:
                # Check types
                if existing[field.name] != field.type:
                    print(
                        f"[{table_name}|{field.name}] Warning! Type mismatch: "
                        f"{existing[field.name]} <> {field.type}"
                    )
                    query = f"ALTER TABLE {table_name} MODIFY COLUMN {field.name} {field.type}"
                    try:
                        connect.execute(post=query)
                    except ClickhouseError as e:
                        print(f"Error when alter Column type: {e};\n Run it Manually: '{query}'")
            else:
                print(f"[{table_name}|{field.name}] Alter column")
                query = f"ALTER TABLE `{table_name}` ADD COLUMN {cls.quote_name(field.name)} {field.type}"
                if after:
                    # None if add before first field
                    query += f" AFTER {cls.quote_name(after)}"
                else:
                    query += " FIRST"
                connect.execute(post=query)
                c = True
            after = field.name
        return c

    @classmethod
    def ensure_table(cls, connect=None):
        changed = False
        ch: "ClickhouseClient" = connect or connection()
        is_cluster = bool(config.clickhouse.cluster)
        table = cls._get_db_table()
        raw_table = cls._get_raw_db_table()
        dist_table = cls._get_distributed_db_table()
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
        if is_cluster:
            print(f"[{table}] Check distributed table")
            if ch.has_table(dist_table):
                changed |= cls.ensure_columns(ch, dist_table)
            else:
                ch.execute(post=cls.get_create_distributed_sql())
                changed = True
        if not ch.has_table(table, is_view=True):
            print(f"[{table}] Synchronize view")
            ch.execute(post=cls.get_create_view_sql())
            changed = True
        return changed
