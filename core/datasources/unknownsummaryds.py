# ----------------------------------------------------------------------
# unknownsummaryds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.inv.models.unknownmodel import UnknownModel


class UnknownSummaryDS(BaseDataSource):
    name = "unknownsummaryds"

    fields = [
        FieldInfo(name="vendor"),
        FieldInfo(name="part_no"),
        FieldInfo(name="description"),
        FieldInfo(name="count", type=FieldType.UINT64),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        data = {}  # vendor, part_no -> description, count
        for c in UnknownModel._get_collection().find():
            vendor = c["vendor"]
            if isinstance(c["vendor"], list):
                # Fix for bad vendor code in DB
                vendor = c["vendor"][0]
            k = (vendor, c["part_no"])
            if k in data:
                data[k][1] += 1
            else:
                data[k] = [c["description"], 1]
        row_num = 0
        for k in data:
            row_num += 1
            yield row_num, "vendor", k[0]
            yield row_num, "part_no", k[1]
            yield row_num, "description", data[k][0]
            yield row_num, "count", data[k][1]
