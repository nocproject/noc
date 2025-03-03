# ----------------------------------------------------------------------
# ReportObjectMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import orjson

# NOC Modules
from .base import CHTableReportDataSource, ReportField


class ReportObjectMetrics(CHTableReportDataSource):
    name = "reportobjectmetrics"
    description = "1"

    TABLE_NAME = "noc.cpu"
    FIELDS = [
        ReportField(
            name="managed_object",
            label="Managed Object BIID",
            description="",
            unit="INT",
            metric_name="managed_object",
            group=True,
        ),
        ReportField(
            name="labels",
            label="Labels",
            description="",
            unit="INT",
            metric_name="labels",
            group=True,
        ),
        ReportField(
            name="cpu_usage",
            label="CPU Usage",
            description="",
            unit="%",
            metric_name="avg(usage)",
        ),
        ReportField(
            name="memory_usage",
            label="Memory Usage",
            description="",
            unit="%",
            metric_name="max(usage)",
        ),
    ]
    TIMEBASED = True

    def get_table(self):
        if "cpu_usage" in self.fields:
            return "noc.cpu"
        elif "memory_usage" in self.fields:
            return "noc.memory"

    def do_query(self):
        """
        Run every query as own, and merge results - iter self.fields
        :return:
        """
        f_date, to_date = self.start, self.end
        result = defaultdict(list)
        client = self.get_client()
        key_fields = [field for field in self.fields if self.fields[field].group]
        for field in list(self.fields):
            if field in key_fields:
                continue
            self.fields = self.get_fields(key_fields + [field])
            query = self.get_query_ch(f_date, to_date, r_format="JSONEachRow")
            # print("Query: %s", query)
            if self.allobjectids or not self.objectids:
                for row in client.execute(query % ""):
                    data = orjson.loads(row[0])
                    mo_id = data.get("managed_object")
                    if mo_id not in result:
                        result[mo_id] = data
                    else:
                        result[mo_id].update(data)
            else:
                # chunked query
                ids = self.objectids
                while ids:
                    chunk, ids = ids[: self.CHUNK_SIZE], ids[self.CHUNK_SIZE :]
                    for row in client.execute(query % f" AND {self.get_object_filter(chunk)}"):
                        data = orjson.loads(row[0])
                        mo_id = data.get("managed_object")
                        if mo_id not in result:
                            result[mo_id] = data
                        else:
                            result[mo_id].update(data)
        self.fields = self.get_fields(self.query_fields)
        for v in result.values():
            yield v
