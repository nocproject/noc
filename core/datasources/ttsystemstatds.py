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
        FieldInfo(name="in_label_2"),
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
        aa = {
            aa.escalation_tt.split(":")[-1]: aa
            for aa in ArchivedAlarm.objects.filter(
                clear_timestamp__gte=start,
                clear_timestamp__lte=end,
                escalation_tt__exists=True,
            )
        }
        row_num = 0
        for ts, server, service, duration, error_code, error_text, in_label in ch.execute(query):
            in_label_2 = in_label
            row_num += 1
            if service in ["create_massive_damage_outer"]:
                # service = "Создание ТТ"
                try:
                    in_label = ManagedObject.objects.get(tt_system_id=int(in_label))
                    in_label_2 = ""
                except ManagedObject.DoesNotExist:
                    pass
                except ManagedObject.MultipleObjectsReturned:
                    in_label = ManagedObject.objects.get(
                        tt_system_id=int(in_label), is_managed=True
                    )
                    in_label_2 = ""
            elif service in ["change_massive_damage_outer_close"]:
                # service = "Закрытие ТТ"
                in_label_2 = in_label
                in_label = aa[in_label].managed_object if in_label in aa else in_label
            else:
                continue
            yield row_num, "ts", ts
            yield row_num, "server", server
            yield row_num, "service", service
            yield row_num, "duration", int(duration)
            yield row_num, "error_code", int(error_code)
            yield row_num, "error_text", error_text
            yield row_num, "in_label", in_label
            yield row_num, "in_label_2", in_label_2

        # q_statistics = TTSystemStatDS.query().groupby(["server", "service"]).agg([
        #     pl.count().alias("req_cnt"),
        #     pl.col("server").filter(pl.col("error_code") == 0).count().alias("succ_cnt"),
        #     pl.col("server").filter(pl.col("error_code") != 0).count().alias("fail_cnt"),
        #     (pl.col("server").filter(pl.col("error_code") == 0).count() / pl.count()).alias("succ_pr"),
        #     (pl.quantile("duration", 0.25) / 1000).alias("q1"),
        #     (pl.quantile("duration", 0.5) / 1000).alias("q2"),
        #     (pl.quantile("duration", 0.75) / 1000).alias("q3"),
        #     (pl.quantile("duration", 0.95) / 1000).alias("p95"),
        #     (pl.max("duration") / 1000).alias("max"),
        # ])

        # q_error_details = TTSystemStatDS.query().filter(pl.col('service').is_in([
        #     'create_massive_damage_outer',
        #     'change_massive_damage_outer_close',
        # ])).select([
        #     "ts", "server", "service", "error_code", "error_text", "in_label", "in_label_2"
        # ])
