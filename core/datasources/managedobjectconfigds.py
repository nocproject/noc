# ----------------------------------------------------------------------
# Managed Object Config Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd
from noc.core.mongo.connection import get_db
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, BaseDataSource


class ManagedObjectConfigDS(BaseDataSource):
    name = "managedobjectconfigds"

    # "Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"
    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
        FieldInfo(name="last_changed_ts", type="datetime64"),
    ]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields)]
        return pd.DataFrame.from_records(data, index="managed_object_id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        pipeline = [
            {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
            {"$sort": {"_id": 1}},
        ]
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
            yield {"managed_object_id": data["_id"], "last_changed_ts": data["last_ts"]}
