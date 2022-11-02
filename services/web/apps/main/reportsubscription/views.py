# ---------------------------------------------------------------------
# main.reportsubscription application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.services.web.app.site import site
from noc.main.models.reportsubscription import ReportSubscription
from noc.core.translation import ugettext as _


class ReportSubscriptionApplication(ExtDocApplication):
    """
    ReportSubscription application
    """

    title = _("Report Subscription")
    menu = [_("Setup"), _("Report Subscription")]
    model = ReportSubscription

    def bulk_field_report_label(self, data):
        """
        Apply report_label field
        :param data:
        :return:
        """
        for x in data:
            x["report__label"] = self.get_reports_map()[x["report"]]
        return data

    def get_reports_map(self):
        if not hasattr(self, "_reports_map"):
            self._reports_map = {}
            for report_id, r in site.iter_predefined_reports():
                self._reports_map[report_id] = r.title
        return self._reports_map
