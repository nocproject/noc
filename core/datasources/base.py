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
from typing import Tuple, Union, Optional, Iterable, List, Dict, AsyncIterable

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


@dataclass
class FieldInfo(object):
    name: str
    description: Optional[str] = None
    internal_name: Optional[str] = None
    type: FieldType = FieldType.STRING
    is_caps: bool = False


class BaseDataSource(object):
    """DataSource and fields description"""

    name: str
    fields: List[FieldInfo]
    row_index = "id"

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
        for f in cls.fields:
            if fields and f.name not in fields:
                continue
            r[f.name] = c_map[f.type]
        return r

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
        return pl.DataFrame(r, columns=[(c.name, c.type.value) for c in cls.fields])

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
                c_row = row_num
                yield r
            r[f_name] = value

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
