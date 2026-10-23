# ----------------------------------------------------------------------
# ReportMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC Modules
from .base import CHTableReportDataSource, ReportField


class ReportAvailability(CHTableReportDataSource):
    name = "reportavailability"
    object_field = "managed_object"
    description = "1"

    TABLE_NAME = "noc.ping"
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
            name="ping_rtt",
            label="Ping RTT (avg)",
            description="",
            unit="MILLISECONDS",
            metric_name="avg(rtt)",
        ),
        ReportField(
            name="ping_attempts",
            label="Ping Attempts",
            description="",
            unit="COUNT",
            metric_name="max(attempts)",
        ),
    ]
    TIMEBASED = True
