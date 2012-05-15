# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reporthistory
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import datetime
import re
## Django modules
from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow,\
                                     SafeString
from noc.main.models import AuditTrail


class ReportHistoryApplication(SimpleReport):
    title = "History"

    class form(forms.Form):
        days = forms.IntegerField(label="Days", initial=3)
        include_prefixes = forms.BooleanField(
            label="Include Prefixes")
        include_addresses = forms.BooleanField(
            label="Include Addresses")

    rx_detail = re.compile(r"^(.+?): (.+?) -> (.+?)$",
        re.MULTILINE | re.UNICODE)

    def format_detail(self, o):
        r = [m.groups() for m in self.rx_detail.finditer(o)]
        s = "<br/>".join(
            "<b>%s</b>: %s &rArr; %s" % (
                self.html_escape(g[0]),
                self.html_escape(g[1]),
                self.html_escape(g[2])) for g in r)
        return SafeString(s)

    def get_data(self, days, include_prefixes,
                 include_addresses,**kwargs):
        dt = datetime.date.today() - datetime.timedelta(days=days)
        scope = []
        if include_prefixes:
            scope += ["ip_prefix"]
        if include_addresses:
            scope += ["ip_address"]
        last = None
        r = []
        for l in AuditTrail.objects.filter(db_table__gte=dt,
                                           db_table__in=scope)\
                                   .order_by("-timestamp")\
                                   .select_related():
            d = l.timestamp.date()
            if d != last:
                last = d
                r += [SectionRow(d.isoformat())]
            r += [(
                l.timestamp.time().strftime("%H:%M:%S"),
                l.user.username,
                {
                    "C": "Create",
                    "M": "Modify",
                    "D": "Delete"
                }[l.operation],
                l.subject,
                self.format_detail(l.body)
            )]

        return self.from_dataset(
            title=self.title,
            columns=["Time", "User", "Action", "Object", "Detail"],
            data=r)
