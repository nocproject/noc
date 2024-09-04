# ---------------------------------------------------------------------
# Unclassified Trap OIDs Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import List, Dict

# Third-party modules
import orjson

# NOC modules
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import Band
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.core.clickhouse.connect import connection
from noc.fm.models.eventclass import EventClass
from noc.fm.models.mib import MIB

SQL = """
    SELECT snmp_trap_oid, count() as cnt
    FROM events
    WHERE event_class = %s AND date >= %s AND snmp_trap_oid != ''
    GROUP BY snmp_trap_oid
    ORDER BY cnt desc
    FORMAT JSONEachRow
"""


class ReportUnclassifiedTrapOIDs(ReportSource):
    name = "reportunclassifiedtrapoids"

    def get_formats(self) -> Dict[str, BandFormat]:
        return {
            "header": BandFormat(title_template="Unclassified Trap OIDs"),
            "row": BandFormat(
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
            ),
        }

    def get_data(self, request=None, **kwargs) -> List[Band]:
        ch = connection()
        data = []
        ec = EventClass.objects.filter(name="Unknown | SNMP Trap").first()
        now = datetime.datetime.now() - datetime.timedelta(days=7)
        r = ch.execute(SQL, args=[ec.bi_id, now.date().isoformat()], return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            b = Band(
                name="row",
                data={
                    "oid": row["snmp_trap_oid"],
                    "name": MIB.get_name(row["snmp_trap_oid"]),
                    "count": row["cnt"],
                },
            )
            data.append(b)
        return data
