# ---------------------------------------------------------------------
# Expiring Domains Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.config import config
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    days = forms.IntegerField(initial=config.dns.warn_before_expired / 86400)


class Reportreportexpiringdomains(SimpleReport):
    title = _("Expiring Domains")
    form = ReportForm

    def get_data(self, request: HttpRequest, days, **kwargs):
        return self.from_query(
            title=self.title,
            columns=[
                _("Domain"),
                TableColumn(_("Expired"), format="bool"),
                TableColumn(_("Paid Till"), format="date"),
            ],
            query=f"""
                SELECT name,paid_till<='now'::date,paid_till
                FROM dns_dnszone
                WHERE paid_till IS NOT NULL
                    AND 'now'::date >= (paid_till-'{int(days)} days'::interval)
                ORDER BY paid_till
            """,
        )
