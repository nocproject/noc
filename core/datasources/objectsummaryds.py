# ----------------------------------------------------------------------
# objectsummaryds datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Any, Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.inv.models.object import Object


class ObjectSummaryDS(BaseDataSource):
    name = "objectsummaryds"

    fields = [
        FieldInfo(name="model"),
        FieldInfo(name="count", type=FieldType.UINT),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Any]]:
        lookup = {
            "from": "noc.objectmodels",
            "localField": "_id",
            "foreignField": "_id",
            "as": "model",
        }
        data = Object._get_collection().aggregate(
            [
                {"$group": {"_id": "$model", "count": {"$sum": 1}}},
                {"$lookup": lookup},
                {"$unwind": "$model"},
                {"$project": {"_id": 0, "model.name": 1, "count": 1}},
            ]
        )
        row_num = 0
        for o in data:
            row_num += 1
            yield row_num, "model", o["model"]["name"]
            yield row_num, "count", o["count"]
