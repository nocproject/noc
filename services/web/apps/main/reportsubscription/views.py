# ---------------------------------------------------------------------
# main.reportsubscription application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.lib.app.site import site
from noc.main.models.reportsubscription import ReportSubscription
from noc.core.translation import ugettext as _


class ReportSubscriptionApplication(ExtDocApplication):
    """
    ReportSubscription application
    """

    title = _("Report Subscription")
    menu = [_("Setup"), _("Report Subscription")]
    model = ReportSubscription

    def field_report__label(self, o):
        return self.get_reports_map()[o.report]

    def get_reports_map(self):
        if not hasattr(self, "_reports_map"):
            self._reports_map = {}
            for report_id, r in site.iter_predefined_reports():
                self._reports_map[report_id] = r.title
        return self._reports_map

    def instance_to_dict(self, o, fields=None, nocustom=False):
        return super().instance_to_dict(o, fields=fields, nocustom=True)
