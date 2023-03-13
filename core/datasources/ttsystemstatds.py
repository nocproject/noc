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
from noc.fm.models.ttsystem import TTSystem

SQL = """
    SELECT ts, server, service, duration, error_code, error_text, in_label
    FROM span
    WHERE server IN (%s)
    AND date >= '%s' AND ts >= toDateTime(%d) AND ts <= toDateTime(%d)
"""


class TTSystemStatDS(BaseDataSource):
    name = "ttsystemstatds"

    fields = [
        FieldInfo(name="ts"),
        FieldInfo(name="server"),
        FieldInfo(name="service"),
        FieldInfo(name="duration", type=FieldType.UINT64),
        FieldInfo(name="error_code", type=FieldType.UINT),
        FieldInfo(name="error_text"),
        FieldInfo(name="in_label"),
    ]

    @classmethod
    async def iter_query(
        cls,
        fields: Optional[Iterable[str]] = None,
        start: datetime.datetime = None,
        end: datetime.datetime = None,
        *args,
        **kwargs,
    ) -> AsyncIterable[Tuple[int, str, Union[str, int]]]:
        now = datetime.datetime.now()
        start = start or now.combine(now.date(), now.min.time())
        end = end or now.combine(now.date(), now.max.time())
        ts_start = time.mktime(start.timetuple())
        ts_end = time.mktime(end.timetuple())
        tt_systems = TTSystem.objects.filter().scalar("name")
        tt_systems = ", ".join([f"'{x}'" for x in tt_systems])
        query = SQL % (tt_systems, start.date().isoformat(), ts_start, ts_end)
        ch = connection()
        row_num = 0
        for row in ch.execute(query):
            row_num += 1
            yield row_num, "ts", row[0]
            yield row_num, "server", row[1]
            yield row_num, "service", row[2]
            yield row_num, "duration", int(row[3])
            yield row_num, "error_code", int(row[4])
            yield row_num, "error_text", row[5]
            yield row_num, "in_label", row[6]

        # q1 = TTSystemStatDS.query().groupby(["server", "service"]).agg([
        #     pl.count(),
        #     pl.quantile("duration", 0.25).alias("q1"),
        #     pl.quantile("duration", 0.5).alias("q2"),
        #     pl.quantile("duration", 0.75).alias("q3"),
        #     pl.quantile("duration", 0.95).alias("p95"),
        #     pl.max("duration").alias("max"),
        # ])
        #
        # q2 = TTSystemStatDS.query().groupby(["server", "service", "error_code"]).agg([
        #     pl.count(),
        #     pl.avg("duration"),
        # ])
        #
        # q3 = TTSystemStatDS.query().filter(pl.col('service').is_in([
        #     'create_massive_damage_outer',
        #     'change_massive_damage_outer_close',
        # ])).select([
        #     "ts", "server", "service", "error_code", "error_text", "in_label"
        # ])
