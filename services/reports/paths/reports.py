# ----------------------------------------------------------------------
# Reports API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Response

REPORTS = {
    # report_name: report_class_name
    "main_reportbackups": "ReportBackups",
    "sa_reportdiscoveryproblem": "ReportFilterApplication",  # Discovery Problem
    "sa_reportobjectsummary": "ReportObjectsSummary",  # Managed Objects Summary: By Profile
    "sa_reportprofilechecksdetailed": "ReportFilterApplication",  # Failed Discovery
    "sa_reportprofilechecksummary": "ReportFilterApplication",  # Managed Object Profile Check Summary
    "sa_reportstalediscovery": "ReportStaleDiscoveryJob",  # Stale discovery
}

router = APIRouter()


@router.get("/api/{report_name}/")
def api_report(report_name):
    report_class_name = REPORTS[report_name]
    m = __import__(
        f"noc.services.reports.report_classes.{report_name}", {}, {}, [report_class_name]
    )
    report_class = getattr(m, report_class_name)
    rep = report_class()

    html = rep.generate_html()
    return Response(content=html, media_type="text/html")
