# ----------------------------------------------------------------------
# Escalations Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
from collections import namedtuple
import datetime
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.platform import Platform
from noc.sa.models.managedobject import ManagedObject

MOInfo = namedtuple("MOInfo", ["name", "address", "platform", "segment"])


class EscalationsDS(BaseDataSource):
    name = "escalationsds"

    fields = [
        FieldInfo(name="timestamp"),
        FieldInfo(name="escalation_timestamp"),
        FieldInfo(name="managed_object"),
        FieldInfo(name="address"),
        FieldInfo(name="platform"),
        FieldInfo(name="segment"),
        FieldInfo(name="tt"),
        FieldInfo(name="objects", type=FieldType.UINT64),
        FieldInfo(name="subscribers", type=FieldType.UINT64),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        start: datetime.datetime = kwargs.get("start")
        end: datetime.datetime = kwargs.get("end")
        q = {
            "timestamp": {"$gte": start, "$lte": end},
            "escalation_tt": {"$exists": True},
        }
        mos = {
            mo[0]: MOInfo(
                name=mo[1],
                address=mo[2],
                platform=str(Platform.get_by_id(mo[3])) if mo[3] else "",
                segment=NetworkSegment.get_by_id(mo[4]).name,
            )
            for mo in ManagedObject.objects.all().values_list(
                "id", "name", "address", "platform", "segment"
            )
        }
        row_num = 0
        for ac in (ActiveAlarm, ArchivedAlarm):
            for d in ac._get_collection().find(q):
                if d["managed_object"] not in mos:
                    continue
                mo = mos[d["managed_object"]]
                row_num += 1
                yield row_num, "timestamp", d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                yield row_num, "escalation_timestamp", d["escalation_ts"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                yield row_num, "managed_object", mo.name.split("#", 1)[0]
                yield row_num, "address", mo.address
                yield row_num, "platform", mo.platform
                yield row_num, "segment", mo.segment
                yield row_num, "tt", d["escalation_tt"]
                yield row_num, "objects", sum(ss["summary"] for ss in d["total_objects"])
                yield row_num, "subscribers", sum(ss["summary"] for ss in d["total_subscribers"])
