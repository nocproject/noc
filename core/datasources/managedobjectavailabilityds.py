# ----------------------------------------------------------------------
# ManagedObject Availability Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
from typing import Optional, Iterable, Tuple, AsyncIterable, Union

# Third-party modules
import orjson
from pymongo.read_preferences import ReadPreference

# NOC modules
from .base import FieldInfo, FieldType, ParamInfo, BaseDataSource
from noc.core.mongo.connection import get_db
from noc.fm.models.reboot import Reboot
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobject import ManagedObject, ManagedObjectStatus

OUTAGES_SQL = """
    SELECT managed_object, min(start) as min_start, max(stop) as max_stop,
     sum(stop - start) as duration_u, count() as unavail_count
    FROM noc.outages
    WHERE (start >= %s or stop >= %s) and start < %s GROUP BY managed_object FORMAT JSONEachRow;
"""


class ManagedObjectAvailabilityDS(BaseDataSource):
    name = "managedobjectavailabilityds"
    row_index = "managed_object_id"

    params = [
        ParamInfo(name="start", type="datetime", required=True),
        ParamInfo(name="end", type="datetime"),
        ParamInfo(name="skip_full_avail", type="bool", default=False),
        ParamInfo(name="skip_zero_avail", type="bool", default=False),
        ParamInfo(name="skip_zero_access", type="bool", default=False),
    ]

    fields = [
        FieldInfo(name="managed_object_id", type=FieldType.UINT),
        FieldInfo(name="id", description="Object Id", type=FieldType.UINT),
        FieldInfo(name="current_avail_status", description="Avail Status", type=FieldType.BOOL),
        FieldInfo(
            name="avail_percent", description="Availability by Percent", type=FieldType.FLOAT
        ),
        FieldInfo(name="downtime", description="Downtime (sec)", type=FieldType.UINT),
        FieldInfo(name="down_count", description="Count outages", type=FieldType.UINT),
        FieldInfo(name="reboots", description="Reboots", type=FieldType.UINT),
    ]

    @staticmethod
    def get_reboots_by_object(start_date: datetime.datetime, stop_date: datetime.datetime):
        """
        Reboots count from interval
        Args:
            start_date:
            stop_date:
        """
        match = {"ts": {"$gte": start_date, "$lte": stop_date}}
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$object", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        data = (
            Reboot._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(pipeline)
        )
        # data = data["result"]
        return {rb["_id"]: rb["count"] for rb in data}

    @staticmethod
    def get_status_outage(
        start_date: datetime.datetime,
        stop_date: datetime.datetime,
        status: bool,
        last: Optional[datetime.datetime] = None,
    ) -> int:
        """
        Convert ManagedObjectStatus to outage interval
        :param start_date: Start interval time
        :param stop_date: End interval time
        :param status: Object Status
        :param last: Last changed status
        :return:
        """
        if status:
            # If device available, zero outage
            return 0
        if not status and (not last or last < start_date):
            # If last less than start interval time - full unavailable
            return int((stop_date - start_date).total_seconds())
        elif not status and start_date < last < stop_date:
            # Last between interval endpoint
            return int((stop_date - last).total_seconds())
        # No outages on interval ?
        return 0

    @staticmethod
    def get_outages_ch(start_date, stop_date):
        from noc.core.clickhouse.connect import connection

        ch = connection()
        outages = {}
        m_biid_map = dict(ManagedObject.objects.filter().values_list("bi_id", "id"))
        r = ch.execute(
            OUTAGES_SQL,
            args=[
                start_date.date().isoformat(),
                stop_date.date().isoformat(),
                stop_date.date().isoformat(),
            ],
            return_raw=True,
        )
        for row in r.split(b"\n"):
            if not row:
                print(row)
                continue
            row = orjson.loads(row)
            oid = m_biid_map.get(int(row["managed_object"]), None)
            if not oid:
                continue
            min_start, max_stop = datetime.datetime.fromisoformat(
                row["min_start"]
            ), datetime.datetime.fromisoformat(row["max_stop"])
            duration = int(row["duration_u"])
            if min_start < start_date:
                duration -= (start_date - min_start).total_seconds()
            if max_stop > stop_date:
                duration -= (max_stop - stop_date).total_seconds()
            outages[oid] = (duration, int(row["unavail_count"]))
        return outages

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        skip_full_avail=False,
        skip_zero_avail=False,
        skip_zero_access=False,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        start, end = cls.clean_interval(start, end)
        td = int((end - start).total_seconds())
        rb = cls.get_reboots_by_object(start_date=start, stop_date=end)
        outages = cls.get_outages_ch(start_date=start, stop_date=end)
        # Getting managed object statuses
        moss = ManagedObjectStatus.objects.all()
        if skip_zero_access:
            ips = list(InterfaceProfile.objects.filter(is_uni=True).scalar("id"))
            pipeline = [
                {"$match": {"profile": {"$in": ips}}},
                {
                    "$group": {
                        "_id": "$managed_object",
                        "m": {"$max": "$oper_status"},
                    }
                },
                {"$match": {"m": False}},
                {"$project": {"_id": True}},
            ]
            data = (
                get_db()["noc.interfaces"]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(pipeline)
            )
            data = [d["_id"] for d in data]
            moss = moss.exclude(managed_object__in=data)
        for num, row in enumerate(moss.values("managed_object", "last", "status")):
            mo_id, status = row["managed_object"], row["status"]
            outage_duration, outage_count = outages.get(mo_id, (0, 0))
            s_outage = cls.get_status_outage(
                start_date=start, stop_date=end, status=status, last=row.get("last")
            )
            if s_outage:
                outage_duration += s_outage
                outage_count += 1
            outage_duration = min(outage_duration, td)
            if skip_full_avail and outage_duration == 0:
                continue
            if skip_zero_avail and outage_duration == td:
                continue
            yield num, "managed_object_id", mo_id
            yield num, "id", mo_id
            yield num, "current_avail_status", row["status"]
            yield num, "avail_percent", (td - outage_duration) * 100.0 / td
            yield num, "downtime", outage_duration
            yield num, "down_count", outage_count
            yield num, "reboots", rb.get(mo_id, 0)
