# ----------------------------------------------------------------------
# Managed Object Config Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Tuple, AsyncIterable

# Third-party modules
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.core.mongo.connection import get_db


class ManagedObjectConfigDS(BaseDataSource):
    name = "managedobjectconfigds"
    row_index = "managed_object_id"

    # "Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="last_changed_ts", type=FieldType.UINT64),
    ]

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        pipeline = [
            {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
            {"$sort": {"_id": 1}},
        ]
        row_num = 0
        # if len(self.sync_ids) < 20000:
        #     # @todo Very large list slowest encode, need research
        #     pipeline.insert(0, {"$match": {"object": {"$in": self.sync_ids}}})
        for data in (
            get_db()["noc.gridvcs.config.files"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(pipeline, allowDiskUse=True)
        ):
            if not data["_id"]:
                continue
            row_num += 1
            yield row_num, "managed_object_id", data["_id"]
            yield row_num, "last_changed_ts", data["last_ts"]
