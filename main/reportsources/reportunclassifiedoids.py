# ---------------------------------------------------------------------
# Unclassified Trap OIDs Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
import orjson

# NOC modules
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import BandData
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.core.clickhouse.connect import connection
from noc.fm.models.eventclass import EventClass

SQL = """
    SELECT 
     snmp_trap_oid,
     dictGetString('noc_dict.eventclass','name', event_class) as event_class_name,
     count() as cnt
    FROM events
    WHERE event_class = %d
    GROUP BY event_class

"""


class ReportUnclassifiedTrapOIDs(ReportSource):
    name = "reportunclassifiedtrapoids"

    def get_format(self) -> BandFormat:
        return BandFormat(
            title_template="Unclassified Trap OIDs",
            columns=[
                ColumnFormat(name="oid", title="OID"),
                ColumnFormat(name="name", title="NAME"),
                ColumnFormat(
                    name="count",
                    title="COUNT",
                    # align="right",
                    total="sum",
                    format_type="integer",
                ),
            ],
        )

    def get_data(self, request=None, **kwargs) -> List[BandData]:
        ch = connection()
        data = []
        ec = EventClass.objects.filter(name="Unknown | SNMP Trap").first()
        r = ch.execute(SQL, args=[ec.bi_id], return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            b = BandData(name="row")
            b.set_data(
                {"oid": row["snmp_trap_oid"], "name": row["event_class_name"], "count": row["cnt"]}
            )
            data.append(b)
        return data
