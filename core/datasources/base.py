# ----------------------------------------------------------------------
# DataSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from functools import partial
from collections import defaultdict
from typing import Tuple, Union, Optional, Iterable, List, Dict, AsyncIterable, Set
from noc.core.wf.diagnostic import DiagnosticState

# Third-party modules
import polars as pl


class FieldType(enum.Enum):
    STRING = pl.Utf8
    INT = pl.Int64
    UINT = pl.UInt32
    UINT64 = pl.UInt64
    INT32 = pl.Int32
    FLOAT = pl.Float32
    BOOL = pl.Boolean
    DATETIME = pl.Datetime


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


class BaseDataSource(object):
    """DataSource and fields description"""

    name: str
    fields: List[FieldInfo]
    row_index = "id"

    @classmethod
    def iter_ds_fields(cls):
        for f in cls.fields:
            yield f

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
        async for _, f_name, value in cls.iter_query(fields, *args, **kwargs):
            r[f_name].append(value)
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
        return pl.DataFrame(
            [
                pl.Series(c.name, r[c.name], dtype=c.type.value)
                for c in cls.iter_ds_fields()
                if len(r[c.name]) and (cls.is_out_field(c, fields) or (c.is_vector and c.name in r))
            ]
        )
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
        async for row_num, f_name, value in cls.iter_query(fields, *args, **kwargs):
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
