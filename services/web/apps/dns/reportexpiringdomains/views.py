# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Expiring Domains Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from django import forms
from noc.settings import config
from noc.core.translation import ugettext as _
#
#
#
class ReportForm(forms.Form):
    days=forms.IntegerField(initial=config.getint("dns","warn_before_expired_days"))
#
#
#
class Reportreportexpiringdomains(SimpleReport):
    title = _("Expiring Domains")
    form=ReportForm
    def get_data(self,days,**kwargs):
        return self.from_query(title=self.title,
            columns=[
                _("Domain"),
                TableColumn(_("Expired"), format="bool"),
                TableColumn(_("Paid Till"), format="date")],
            query="""
                SELECT name,paid_till<='now'::date,paid_till
                FROM dns_dnszone
                WHERE paid_till IS NOT NULL
                    AND 'now'::date >= (paid_till-'%d days'::interval)
                ORDER BY paid_till
            """%days)
