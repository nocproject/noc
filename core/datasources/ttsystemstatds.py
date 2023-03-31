# ----------------------------------------------------------------------
# TTSystemStat Datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python Modules
import datetime
import time
from typing import Optional, Iterable, Tuple, AsyncIterable, Union

# NOC modules
from .base import FieldInfo, FieldType, BaseDataSource
from noc.core.clickhouse.connect import connection
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.sa.models.managedobject import ManagedObject

SQL = """
    SELECT ts, server, service, duration, error_code, error_text, in_label as tt_id
    FROM span
    WHERE server IN (%s)
    AND date >= '%s' AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
"""


class TTSystemStatDS(BaseDataSource):
    """
    Queries for reports

    TT system statistics
    --------------------
    TTSystemStatDS.query().groupby(["server", "service"]).agg([
        pl.count().alias("req_cnt"),
        pl.col("server").filter(pl.col("error_code") == 0).count().alias("succ_cnt"),
        pl.col("server").filter(pl.col("error_code") != 0).count().alias("fail_cnt"),
        (pl.col("server").filter(pl.col("error_code") == 0).count() / pl.count()).alias("succ_pr"),
        (pl.quantile("duration", 0.25) / 1000).alias("q1"),
        (pl.quantile("duration", 0.5) / 1000).alias("q2"),
        (pl.quantile("duration", 0.75) / 1000).alias("q3"),
        (pl.quantile("duration", 0.95) / 1000).alias("p95"),
        (pl.max("duration") / 1000).alias("max"),
    ])

    TT system error detalization
    ----------------------------
    TTSystemStatDS.query().filter(pl.col('service').is_in([
        'create_massive_damage_outer',
        'change_massive_damage_outer_close',
    ])).select([
        "ts", "server", "service", "error_code", "error_text", "managed_object", "tt_id"
    ])
    """

    name = "ttsystemstatds"

    fields = [
        FieldInfo(name="ts"),
        FieldInfo(name="server"),
        FieldInfo(name="service"),
        FieldInfo(name="duration", type=FieldType.UINT64),
        FieldInfo(name="error_code", type=FieldType.UINT),
        FieldInfo(name="error_text"),
        FieldInfo(name="managed_object"),
        FieldInfo(name="tt_id"),
    ]

    @classmethod
    async def iter_query(
        cls,
        start: datetime.datetime,
        end: datetime.datetime,
        fields: Optional[Iterable[str]] = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        ts_start = time.mktime(start.timetuple())
        ts_end = time.mktime(end.timetuple())
        tt_systems = TTSystem.objects.filter().scalar("name")
        tt_systems = ", ".join([f"'{x}'" for x in tt_systems])
        query = SQL % (tt_systems, start.date().isoformat(), ts_start, ts_end)
        ch = connection()
        mos_aa = {
            aa[0].split(":")[-1]: aa[1].name
            for aa in ArchivedAlarm.objects.filter(
                clear_timestamp__gte=start,
                clear_timestamp__lte=end,
                escalation_tt__exists=True,
            ).values_list("escalation_tt", "managed_object")
        }
        mos = dict(
            ManagedObject.objects.filter(tt_system_id__isnull=False)
            .values_list("tt_system_id", "name")
            .order_by("is_managed")
        )
        row_num = 0
        for ts, server, service, duration, error_code, error_text, tt_id in ch.execute(query):
            if service == "create_massive_damage_outer":
                managed_object = mos.get(tt_id, "")
                if managed_object:
                    tt_id = ""
            elif service == "change_massive_damage_outer_close":
                managed_object = mos_aa.get(tt_id, tt_id)
            else:
                continue
            row_num += 1
            yield row_num, "ts", ts
            yield row_num, "server", server
            yield row_num, "service", service
            yield row_num, "duration", int(duration)
            yield row_num, "error_code", int(error_code)
            yield row_num, "error_text", error_text
            yield row_num, "managed_object", managed_object
            yield row_num, "tt_id", tt_id
