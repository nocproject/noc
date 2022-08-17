# ----------------------------------------------------------------------
# Managed Object Location Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any

# Third-party modules
import pandas as pd
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject


class ManagedObjectLocationDS(BaseDataSource):
    name = "managedobjectlocationds"

    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
        FieldInfo(name="container_id", type="int64"),
        FieldInfo(name="location_address"),
    ]

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields, **args, **kwargs)]
        return pd.DataFrame.from_records(data, index="container_id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:
        match = {"data.interface": "address"}
        value = (
            Object._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {
                        "$project": {
                            "data": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "d1",
                                    "cond": {
                                        "$and": [
                                            {"$eq": ["$$d1.interface", "address"]},
                                            {
                                                "$or": [
                                                    {"$not": ["$$d1.scope"]},
                                                    {"$eq": ["$$d1.scope", ""]},
                                                ]
                                            },
                                            {"$eq": ["$$d1.attr", "text"]},
                                        ]
                                    },
                                }
                            },
                            "parent_name": "$name",
                        }
                    },
                    {
                        "$project": {
                            "parent_address": {"$arrayElemAt": ["$data.value", 0]},
                            "parent_name": 1,
                            "_id": 1,
                        }
                    },
                    {
                        "$lookup": {
                            "from": "noc.objects",
                            "localField": "_id",
                            "foreignField": "container",
                            "as": "child_cont",
                        }
                    },
                    {
                        "$project": {
                            "parent_address": 1,
                            "parent_name": 1,
                            "_id": 1,
                            "child_cont._id": 1,
                            "child_cont.name": 1,
                        }
                    },
                    {"$unwind": {"path": "$child_cont", "preserveNullAndEmptyArrays": True}},
                ]
            )
        )
        r = {}
        managed_object_map = {
            container: mo_id
            for mo_id, container in (ManagedObject.objects.filter().values_list("id", "container"))
        }
        for v in value:
            cid = str(v["_id"])
            if "child_cont" in v and "parent_address" in v and str(v["child_cont"]["_id"]) not in r:
                # r[str(v["child_cont"]["_id"])] = v["parent_address"].strip()
                # cont_map[str(v["child_cont"]["_id"])] = v["parent_address"].strip()
                r = {
                    "container_id": str(v["child_cont"]["_id"]),
                    "location_address": v["parent_address"].strip(),
                }
                if r["container_id"] in managed_object_map:
                    r["managed_object_id"] = managed_object_map[r["container_id"]]
                yield r
            if cid not in r and "parent_address" in v:
                # r[cid] = v["parent_address"].strip()
                r = {"container_id": cid, "location_address": v["parent_address"].strip()}
                if r["container_id"] in managed_object_map:
                    r["managed_object_id"] = managed_object_map[r["container_id"]]
                yield r

        # for mo_id, container in (
        #         ManagedObject.objects.filter(id__in=self.sync_ids)
        #                 .values_list("id", "container")
        #                 .order_by("id")
        # ):
        #     if container in r:
        #         yield mo_id, r[container]
        #     elif container in cont_map:
        #         yield mo_id, cont_map[container]
