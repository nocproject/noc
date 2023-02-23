# ----------------------------------------------------------------------
# main.report application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.report import Report
from noc.core.translation import ugettext as _


class ReportApplication(ExtDocApplication):
    """
    Report application
    """

    title = "Reports"
    menu = _("Report")
    model = Report

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields, nocustom)
        if isinstance(o, Report):
            bands = []
            for b in r["bands"]:
                if b["name"] == "Root":
                    r["root_orientation"] = b.get("orientation")
                    r["root_queries"] = b.get("queries") or []
                    continue
                bands += [b]
            r["bands"] = bands
        return r

    def clean(self, data):
        root_orientation = data.pop("orientation", None)
        root_queries = data.pop("queries", None)
        data["bands"] += [{
            "name": "Root",
            "orientation": data.pop("root_orientation", None) or "H",
            "queries": data.pop("root_queries", None) or [],
        }]
        return super().clean(data)
