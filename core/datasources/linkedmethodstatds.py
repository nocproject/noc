# ----------------------------------------------------------------------
# Linked Methods Stats Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from noc.inv.models.link import Link

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource


class LinkedMethodStatDS(BaseDataSource):
    name = "linkedmethodstatds"

    fields = [
        FieldInfo(name="pool"),
        FieldInfo(name="method"),
        FieldInfo(name="count", type=FieldType.UINT),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        for num, x in enumerate(
            Link._get_collection().aggregate(
                [
                    {"$group": {"_id": "$discovery_method", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        ):
            yield num, "pool", "-"
            yield num, "method", x["_id"]
            yield num, "count", x["count"]
