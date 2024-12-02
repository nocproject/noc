# ----------------------------------------------------------------------
# Interface MACs Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, AsyncIterable, Tuple

# Third-party modules
import orjson

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
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

    row_index = ("managed_object_id", "interface_name")

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="interface_name"),
        FieldInfo(name="mac_count", type=FieldType.UINT),
        FieldInfo(name="macs", type=FieldType.LIST_STRING),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: "datetime.datetime" = None,
        end: "datetime.datetime" = None,
        resolve_managedobject_id: bool = True,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
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
        for row_num, row in enumerate(result.splitlines(), start=1):
            row = orjson.loads(row)
            if resolve_managedobject_id:
                yield row_num, "managed_object_id", int(row["managed_object_id"])
            else:
                yield row_num, "managed_object_id", int(row["managed_object"])
            yield row_num, "interface_name", row["interface"]
            yield row_num, "mac_count", int(row["mac_count"])
