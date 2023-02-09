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
    "reportdiscoveryproblem": "ReportFilterApplication",  # Discovery Problem
    "reportobjectsummary": "ReportObjectsSummary",  # Managed Objects Summary: By Profile
    "reportprofilechecksdetailed": "ReportFilterApplication",  # Failed Discovery
    "reportprofilechecksummary": "ReportFilterApplication",  # Managed Object Profile Check Summary
    "reportstalediscovery": "ReportStaleDiscoveryJob",  # Stale discovery
}

router = APIRouter()


@router.get("/api/{report_name}/")
def api_report(report_name):
    report_class_name = REPORTS[report_name]
    m = __import__(
        f"noc.services.reportstest.report_classes.{report_name}", {}, {}, [report_class_name]
    )
    report_class = getattr(m, report_class_name)
    rep = report_class()
    if report_name == "reportobjectsummary":
        html = rep.report_html(request=None, report_type="profile")
    else:
        html = rep.report_html(request=None)
    return Response(content=html, media_type="text/html")
