# ----------------------------------------------------------------------
# ReportObjectMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

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
