# ----------------------------------------------------------------------
# Interface Status Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Any, List

# Third-party modules
import pandas as pd
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, BaseDataSource
from noc.inv.models.interface import Interface


class InterfacesStatusStatDS(BaseDataSource):
    name = "interfacesstatusstat"

    # "Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"
    fields = [
        FieldInfo(name="managed_object_id", type="int64"),
        FieldInfo(name="Up_10G", type="int64"),
        FieldInfo(name="Up_1G", type="int64"),
        FieldInfo(name="Up_100M", type="int64"),
        FieldInfo(name="Up_10M", type="int64"),
        FieldInfo(name="Down_-", type="int64"),
        FieldInfo(name="-", type="int64"),
    ]

    @staticmethod
    def humanize_speed(speed: Optional[int]) -> str:
        if not speed:
            return "-"
        for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
            if speed >= t:
                if speed // t * t == speed:
                    return "%d%s" % (speed // t, n)
                else:
                    return "%.2f%s" % (float(speed) / t, n)
        return str(speed)

    @classmethod
    def get_result(cls, fields: Dict[str, int], statuses: List[Dict[str, int]]) -> Dict[str, int]:
        # @todo Column filter
        r = fields.copy()
        for ss in statuses:
            oper_status = {True: "Up", False: "Down", None: "-"}[ss.get("oper_status")]
            key = f'{oper_status}_{cls.humanize_speed(ss.get("in_speed"))}'
            if key in fields:
                r[key] = int(ss["count"])
        return r

    @classmethod
    async def query(cls, fields: Optional[Iterable[str]] = None, *args, **kwargs) -> pd.DataFrame:
        data = [mm async for mm in cls.iter_query(fields)]
        return pd.DataFrame.from_records(data, index="managed_object_id")

    @classmethod
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> Iterable[Dict[str, Any]]:

        match = {"type": "physical"}
        query_fields = {ff.name: None for ff in cls.fields if not fields or ff.name in fields}
        for data in (
            Interface._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {
                        "$group": {
                            "_id": {
                                "in_speed": "$in_speed",
                                "managed_object": "$managed_object",
                                "oper_status": "$oper_status",
                            },
                            "count": {"$sum": 1},
                        }
                    },
                    {
                        "$project": {
                            "in_speed": "$_id.in_speed",
                            "oper_status": "$_id.oper_status",
                            "count": 1,
                            "_id": 0,
                            "managed_object": "$_id.managed_object",
                        }
                    },
                    {
                        "$group": {
                            "_id": "$managed_object",
                            "result": {
                                "$push": {
                                    "count": "$count",
                                    "in_speed": "$in_speed",
                                    "oper_status": "$oper_status",
                                }
                            },
                        }
                    },
                ],
                allowDiskUse=True,
            )
        ):
            r = cls.get_result(query_fields, data["result"])
            r["managed_object_id"] = data["_id"]
            yield r
