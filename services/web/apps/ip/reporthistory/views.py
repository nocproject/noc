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
from noc.lib.app.simplereport import (SimpleReport, SectionRow,
                                      SafeString)
from noc.main.models.audittrail import AuditTrail
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address


class ReportHistoryApplication(SimpleReport):
    title = "History"

    class form(forms.Form):
        days = forms.IntegerField(label="Days", initial=3)
        include_prefixes = forms.BooleanField(
            label="Include Prefixes",
            required=False
        )
        include_addresses = forms.BooleanField(
            label="Include Addresses",
            required=False
        )

    rx_detail = re.compile(r"^(.+?): (.+?) -> (.+?)$",
        re.MULTILINE | re.UNICODE)

    MODELS = {
        "ip.Prefix": Prefix,
        "ip.Address": Address
    }

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
            scope += ["ip.Prefix"]
        if include_addresses:
            scope += ["ip.Address"]
        last = None
        r = []
        for l in AuditTrail.objects.filter(timestamp__gte=dt,
                                           model_id__in=scope)\
                                   .order_by("-timestamp"):
            d = l.timestamp.date()
            if d != last:
                last = d
                r += [SectionRow(d.isoformat())]
            model = self.MODELS[l.model_id]
            if l.object:
                try:
                    obj = unicode(model.objects.get(id=int(l.object)))
                except model.DoesNotExist:
                    obj = "UNKNOWN?"
            else:
                obj = "?"
            chg = []
            for c in l.changes:
                if c.old is None and c.new is None:
                    continue
                chg += ["%s: %s -> %s" % (c.field, c.old, c.new)]
            r += [(
                self.to_json(l.timestamp),
                l.user,
                {
                    "C": "Create",
                    "U": "Modify",
                    "M": "Modify",
                    "D": "Delete"
                }[l.op],
                obj,
                self.format_detail("\n".join(chg))
            )]

        return self.from_dataset(
            title=self.title,
            columns=["Time", "User", "Action", "Object", "Detail"],
            data=r)
