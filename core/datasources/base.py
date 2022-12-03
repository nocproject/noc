# ----------------------------------------------------------------------
# DataSource Base
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from functools import partial
from collections import defaultdict
from typing import Tuple, Union, Optional, Iterable, List, Dict, AsyncIterable

# Third-party modules
import polars as pl


@dataclass
class FieldInfo(object):
    name: str
    description: Optional[str] = None
    internal_name: Optional[str] = None
    type: str = "string"
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
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pl.DataFrame:
        """
        Method for query report data. Return pandas dataframe.
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """
        r = defaultdict(list)
        async for f_name, value in cls.iter_query(fields, *args, **kwargs):
            r[f_name].append(value)
        return pl.DataFrame(r)

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
        c_id = None
        async for f_name, value in cls.iter_query(fields, *args, **kwargs):
            if f_name == cls.row_index and value != c_id:
                c_id = value
                yield r
            r[f_name] = value

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, Union[str, int]]]:
        """
        Method for query report data. Iterate over field data
        :param fields: list fields for filtered on query
        :param args: arguments for report query
        :param kwargs:
        :return:
        """
        ...
