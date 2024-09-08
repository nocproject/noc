# ---------------------------------------------------------------------
# Event Summary Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List, Dict

# Third-party modules
import orjson

# NOC modules
from noc.core.reporter.reportsource import ReportSource
from noc.core.reporter.report import Band
from noc.core.reporter.types import BandFormat, ColumnFormat
from noc.core.clickhouse.connect import connection

SQL = """
    SELECT
     %s AS object,
     count() as quantity
    FROM events
    GROUP BY object
    ORDER BY quantity DESC
    LIMIT 100
    FORMAT JSONEachRow
"""


class ReportEventSummary(ReportSource):
    name = "reporteventsummary"

    def get_formats(self) -> Dict[str, BandFormat]:
        return {
            "header": BandFormat(title_template="Event Summary"),
            "row": BandFormat(
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
            ),
        }

    def get_data(self, request=None, **kwargs) -> List[Band]:
        """ """
        report_type = kwargs.get("report_type") or []
        if "class" in report_type:
            obj_field = "dictGetString('noc_dict.eventclass','name', event_class)"
        elif "object" in report_type:
            obj_field = "dictGetString('noc_dict.managedobject','name', managed_object)"
        elif "profile" in report_type:
            obj_field = "dictGetString('noc_dict.managedobject','profile', managed_object)"
        else:
            raise Exception("Invalid report type: %s" % report_type)
        ch = connection()
        data = []
        r = ch.execute(SQL % obj_field, return_raw=True)
        for row in r.splitlines():
            row = orjson.loads(row)
            b = Band(name="row", data={"object": row["object"], "quantity": row["quantity"]})
            data.append(b)
        return data
