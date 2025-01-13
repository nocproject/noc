# ----------------------------------------------------------------------
# Reboots Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from django.db import connection

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.fm.models.reboot import Reboot


class RebootsDS(BaseDataSource):
    name = "rebootsds"

    fields = [
        FieldInfo(name="managed_object", type=FieldType.UINT),
        FieldInfo(name="address"),
        FieldInfo(name="reboots", type=FieldType.UINT64),
    ]

    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        time_cond = {}
        start, end = cls.clean_interval(start, end)
        if start:
            time_cond["$gte"] = start
        if end:
            time_cond["$lte"] = end
        match = {"ts": time_cond} if time_cond else {}
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$object", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        data = list(Reboot._get_collection().aggregate(pipeline))
        # Get names and addresses from sa_managedobject
        ids = [x["_id"] for x in data]
        mo_names = {}
        cursor = connection.cursor()
        while ids:
            chunk = [str(x) for x in ids[:500]]
            ids = ids[500:]
            cursor.execute(
                f"""
                SELECT id, name, address
                FROM sa_managedobject
                WHERE id IN ({", ".join(chunk)})"""
            )
            mo_names.update({c[0]: c[1:3] for c in cursor})
        #
        row_num = 0
        for row in data:
            row_num += 1
            yield row_num, "managed_object", mo_names.get(row["_id"], "---")[0]
            yield row_num, "address", mo_names.get(row["_id"], "---")[1]
            yield row_num, "reboots", row["count"]
