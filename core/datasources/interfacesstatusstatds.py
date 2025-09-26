# ----------------------------------------------------------------------
# Interface Status Stat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from typing import Optional, Iterable, Dict, Tuple, List, AsyncIterable

# Third-party modules
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.inv.models.interface import Interface


class InterfacesStatusStatDS(BaseDataSource):
    name = "interfacesstatusstatds"
    row_index = "managed_object_id"

    # "Up/10G", "Up/1G", "Up/100M", "Up/10M", "Down/-", "-"
    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="Up_10G", type=FieldType.UINT),
        FieldInfo(name="Up_1G", type=FieldType.UINT),
        FieldInfo(name="Up_100M", type=FieldType.UINT),
        FieldInfo(name="Up_10M", type=FieldType.UINT),
        FieldInfo(name="Down_-", type=FieldType.UINT),
        FieldInfo(name="-", type=FieldType.UINT),
    ]

    @staticmethod
    def humanize_speed(speed: Optional[int]) -> str:
        if not speed:
            return "-"
        for t, n in [(1000000, "G"), (1000, "M"), (1, "k")]:
            if speed >= t:
                if speed // t * t == speed:
                    return "%d%s" % (speed // t, n)
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
    async def iter_query(
        cls, fields: Optional[Iterable[str]] = None, *args, **kwargs
    ) -> AsyncIterable[Tuple[str, str]]:
        match = {"type": "physical"}
        query_fields = {ff.name: None for ff in cls.fields if not fields or ff.name in fields}
        row_num = 0
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
            row_num += 1
            r = cls.get_result(query_fields, data["result"])
            yield row_num, "managed_object_id", data["_id"]
            yield row_num, "Up_10G", r.get("Up_10G", 0)
            yield row_num, "Up_1G", r.get("Up_1G", 0)
            yield row_num, "Up_100M", r.get("Up_100M", 0)
            yield row_num, "Up_10M", r.get("Up_10M", 0)
            yield row_num, "Down_-", r.get("Down_-", 0)
            yield row_num, "-", r.get("-", 0)
