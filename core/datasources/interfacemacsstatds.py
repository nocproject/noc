# ----------------------------------------------------------------------
# Interface MACs Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd
import orjson

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.core.clickhouse.connect import connection
from noc.config import config

SQL = f"""
   SELECT dictGetUInt64('{config.clickhouse.db_dictionaries}.managedobject', 'id', managed_object) as managed_object_id,
    managed_object,  interface, uniqExact(mac) as mac_count
   FROM mac
   WHERE date >= '%s' and date < '%s'
    GROUP BY managed_object, interface FORMAT JSONEachRow 
"""

DEFAULT_INTERVAL = 86400


class InterfaceMACsStatDS(BaseDataSource):
    name = "interfacemacsstatds"

    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
        FieldInfo(name="interface_name", type="str"),
        FieldInfo(name="mac_count", type="int64"),
    ]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, *args, **kwargs)]
        return pd.DataFrame.from_records(data, index=["managed_object_id", "interface_name"])

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: "datetime.datetime" = None,
        end: "datetime.datetime" = None,
        resolve_managedobject_id: bool = True,
        *args,
        **kwargs,
    ) -> Iterable[Dict[str, Any]]:
        """

        :param fields:
        :param start:
        :param end:
        :param resolve_managedobject_id:
        :param args:
        :param kwargs:
        :return:
        """
        end = end or datetime.datetime.now()
        start = start or end - datetime.timedelta(seconds=DEFAULT_INTERVAL)
        ch = connection()
        result = ch.execute(
            SQL % (start.date().isoformat(), end.date().isoformat()), return_raw=True
        )
        for row in result.splitlines():
            row = orjson.loads(row)
            yield {
                "managed_object_id": int(row["managed_object_id"])
                if resolve_managedobject_id
                else int(row["managed_object"]),
                "interface_name": row["interface"],
                "mac_count": int(row["mac_count"]),
            }
