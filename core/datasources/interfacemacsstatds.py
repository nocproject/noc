# ----------------------------------------------------------------------
# Interface MACs Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, AsyncIterable, Tuple

# Third-party modules
import orjson

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.core.clickhouse.connect import connection
from noc.config import config
from noc.inv.models.macvendor import MACVendor
from noc.core.mac import MAC
from noc.ip.models.address import Address

SQL = f"""
   SELECT dictGetUInt64('{config.clickhouse.db_dictionaries}.managedobject', 'id', managed_object) as managed_object_id,
    managed_object,  interface, uniqExact(mac) as mac_count, groupUniqArray(10)(mac) as macs
   FROM mac
   WHERE date >= '%s' and date <= '%s'
   GROUP BY managed_object, interface
   FORMAT JSONEachRow
"""

DEFAULT_INTERVAL = 2 * 86400


class InterfaceMACsStatDS(BaseDataSource):
    name = "interfacemacsstatds"

    row_index = ("managed_object_id", "interface_name")

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="interface_name"),
        FieldInfo(name="mac_count", type=FieldType.UINT),
        FieldInfo(name="macs", type=FieldType.LIST_STRING),
        FieldInfo(name="first_mac"),
        FieldInfo(name="one_vendor"),
        FieldInfo(name="one_address"),
        FieldInfo(name="two_vendor"),
        FieldInfo(name="two_address"),
    ]

    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime"),
        ParamInfo(name="resolve_managedobject_id", type="bool", default=True),
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
        ip_mac_binding = dict(
            Address.objects.filter().exclude(mac=None).values_list("mac", "address")
        )
        start, end = cls.clean_interval(start, end)
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
            macs = [str(MAC(int(m))) for m in row["macs"]]
            yield row_num, "macs", macs[:3]
            yield row_num, "first_mac", macs[0]
            if 1 <= len(macs) < 3:
                yield row_num, "one_address", ip_mac_binding.get(macs[0], "")
                yield row_num, "one_vendor", MACVendor.get_vendor(macs[0])
                if len(macs) == 2:
                    yield row_num, "two_address", ip_mac_binding.get(macs[1], "")
                    yield row_num, "two_vendor", MACVendor.get_vendor(macs[1])
                else:
                    yield row_num, "two_address", ""
                    yield row_num, "two_vendor", ""
            else:
                yield row_num, "one_address", ""
                yield row_num, "one_vendor", ""
                yield row_num, "two_address", ""
                yield row_num, "two_vendor", ""
