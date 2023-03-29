# ----------------------------------------------------------------------
# Escalations Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, Tuple, AsyncIterable

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.sa.models.managedobject import ManagedObject


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
        from_date: datetime.date,
        to_date: datetime.date,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[str, str]]:
        now = datetime.datetime.now()
        t0 = now.combine(from_date, now.min.time())
        t1 = now.combine(to_date, now.max.time())
        q = {
            "timestamp": {"$gte": t0, "$lte": t1},
            "escalation_tt": {"$exists": True},
        }
        row_num = 0
        for ac in (ActiveAlarm, ArchivedAlarm):
            for d in ac._get_collection().find(q):
                mo = ManagedObject.get_by_id(d["managed_object"])
                if not mo:
                    continue
                row_num += 1
                yield row_num, "timestamp", d["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                yield row_num, "escalation_timestamp", d["escalation_ts"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                yield row_num, "managed_object", mo.name.split("#", 1)[0]
                yield row_num, "address", mo.address
                yield row_num, "platform", mo.platform
                yield row_num, "segment", mo.segment.name
                yield row_num, "tt", d["escalation_tt"]
                yield row_num, "objects", sum(ss["summary"] for ss in d["total_objects"])
                yield row_num, "subscribers", sum(ss["summary"] for ss in d["total_subscribers"])
