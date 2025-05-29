# ----------------------------------------------------------------------
# DataSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
import datetime
from time import perf_counter
from dataclasses import dataclass
from functools import partial
from collections import defaultdict
from typing import Tuple, Union, Optional, Iterable, List, Dict, AsyncIterable, Set, Any

# Third-party modules
import polars as pl

# NOC modules
from noc.core.wf.diagnostic import DiagnosticState
from noc.models import get_model

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


@dataclass
class ParamInfo:
    """Datasource Params description"""

    name: str
    type: str  # str, int, float, date, time
    required: bool = False
    allow_multi: bool = False
    resolve_nester: bool = True
    display_label: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    model: Optional[str] = None

    def clean_value(self, value: Union[str, List[str]]):
        if not isinstance(value, list):
            value = [value]
        if self.model and self.resolve_nester and self.allow_multi:
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
        elif self.type == "datetime" and isinstance(value, datetime.datetime):
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

    name: str
    fields: List[FieldInfo]
    params: Optional[List[ParamInfo]] = None
    row_index: Union[str, Tuple[str, ...]] = "id"

    @classmethod
    def join_fields(cls) -> List[str]:
        if not cls.row_index:
            return []
        if cls.row_index and isinstance(cls.row_index, str):
            return [cls.row_index]
        return list(cls.row_index)

    @classmethod
    def iter_ds_fields(cls):
        for f in cls.fields:
            yield f

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
        for f in cls.iter_ds_fields():
            if f.name == name:
                return True
        return False

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
        elif cls.row_index and f.name == cls.row_index:
            return True
        elif f.name not in fields:
            # Not filtered field
            return False
        return True

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pl.DataFrame:
        """
        Method for query report data. Return pandas dataframe.
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
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
        series = []
        for c in cls.iter_ds_fields():
            if len(r[c.name]) and (cls.is_out_field(c, fields) or (c.is_vector and c.name in r)):
                try:
                    series.append(pl.Series(c.name, r[c.name], dtype=c.type.value))
                except TypeError:
                    print(f"Type Error on column: {c.name}. Will be skipping")
                except OverflowError:
                    print(f"OverflowError on column: {c.name}. Will be skipping")
                except pl.exceptions.InvalidOperationError:
                    print(f"Invalid Operation Cast on column: {c.name}. Will be skipping")
        return pl.DataFrame(series)
        # return pl.DataFrame(r, columns=[(c.name, c.type.value) for c in cls.fields])

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
        ...

    @classmethod
    def clean_row_value(cls, value):
        return value
