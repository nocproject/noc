# ----------------------------------------------------------------------
# ReportMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from .base import CHTableReportDataSource, ReportField


class ReportAvailability(CHTableReportDataSource):
    name = "reportavailability"
    description = "1"

    TABLE_NAME = "noc.ping"
    FIELDS = [
        ReportField(
            name="ping_rtt_avg",
            label="ping_rtt",
            description="",
            unit="MILLISECONDS",
            metric_name="avg(rtt)",
        ),
        ReportField(
            name="ping_attemtps_max",
            label="ping_rtt",
            description="",
            unit="COUNT",
            metric_name="max(rtt)",
        ),
    ]
    TIMEBASED = True
