# ---------------------------------------------------------------------
# Event Summary Report
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

SQL = """
    SELECT
     dictGetString('noc_dict.eventclass','name', event_class) as object,
     count() as quantity
    FROM events
    GROUP BY event_class
    ORDER BY quantity
    LIMIT 100
    FORMAT JSONEachRow
"""


class ReportEventSummary(ReportSource):
    name = "reporteventsummary"

    def get_format(self) -> BandFormat:
        return BandFormat(
            title_template="Event Summary",
            columns=[
                ColumnFormat(name="object", title="Object"),
                ColumnFormat(
                    name="quantity",
                    title="Quantity",
                    # align="right",
                    total="sum",
                    format_type="integer",
                ),
            ],
        )

    def get_data(self, request=None, **kwargs) -> List[BandData]:
        """ """
        report_type = kwargs.get("report_type")
        ch = connection()
        data = []
        r = ch.execute(SQL, return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            b = BandData(name="row")
            b.set_data({"object": row["object"], "quantity": row["quantity"]})
            data.append(b)
        return data
