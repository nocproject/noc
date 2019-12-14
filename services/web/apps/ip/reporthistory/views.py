# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ip.reporthistory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
import datetime
import re

# Third-party modules
from django import forms
from noc.core.translation import ugettext as _

# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, SafeString
from noc.main.models.audittrail import AuditTrail
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address


class ReportHistoryApplication(SimpleReport):
    title = _("History")

    class form(forms.Form):
        days = forms.IntegerField(label="Days", initial=3)
        date_from = forms.DateField(
            label="Date from (YYYY-MM-DD)",
            required=False,
            help_text="If empty, the Days parameter will be used",
        )
        date_to = forms.DateField(
            label="Date to (YYYY-MM-DD)",
            initial=datetime.date.today(),
            required=False,
            help_text="If empty, the Days parameter will be used",
        )
        search_ip = forms.CharField(label="Search by ip", required=False)
        search_prefix = forms.CharField(label="Search by prefix", required=False)
        search_user = forms.CharField(label="Search by user", required=False)
        include_prefixes = forms.BooleanField(
            label="Include Prefixes", required=False, initial=True
        )
        include_addresses = forms.BooleanField(
            label="Include Addresses", required=False, initial=True
        )

    rx_detail = re.compile(r"^(.+?): (.+?) -> (.+?)$", re.MULTILINE | re.UNICODE)

    MODELS = {"ip.Prefix": Prefix, "ip.Address": Address}

    def format_detail(self, o):
        r = [m.groups() for m in self.rx_detail.finditer(o)]
        s = "<br/>".join(
            "<b>%s</b>: %s &rArr; %s"
            % (self.html_escape(g[0]), self.html_escape(g[1]), self.html_escape(g[2]))
            for g in r
        )
        return SafeString(s)

    def get_data(
        self,
        days,
        date_from,
        date_to,
        include_prefixes,
        search_ip,
        search_prefix,
        search_user,
        include_addresses,
        **kwargs
    ):
        scope = []
        if include_prefixes:
            scope += ["ip.Prefix"]
        if include_addresses:
            scope += ["ip.Address"]
        last = None
        r = []
        if date_from and date_to:
            audit_trail = AuditTrail.objects.filter(
                timestamp__gte=date_from,
                timestamp__lte=date_to + datetime.timedelta(days=1),
                model_id__in=scope,
            ).order_by("-timestamp")
        else:
            dt = datetime.date.today() - datetime.timedelta(days=days)
            audit_trail = AuditTrail.objects.filter(timestamp__gte=dt, model_id__in=scope).order_by(
                "-timestamp"
            )
        if search_ip:
            try:
                audit_trail = audit_trail.filter(
                    object=str(Address.objects.get(address=search_ip).id)
                )
            except Address.DoesNotExist:
                audit_trail = audit_trail.none()
        if search_prefix:
            try:
                audit_trail = audit_trail.filter(
                    object=str(Prefix.objects.get(prefix=search_prefix).id)
                )
            except Prefix.DoesNotExist:
                audit_trail = audit_trail.none()
        if search_user:
            audit_trail = audit_trail.filter(user__iexact=search_user)
        for l in audit_trail:
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
            r += [
                (
                    self.to_json(l.timestamp),
                    l.user,
                    {"C": "Create", "U": "Modify", "M": "Modify", "D": "Delete"}[l.op],
                    obj,
                    self.format_detail("\n".join(chg)),
                )
            ]

        return self.from_dataset(
            title=self.title, columns=["Time", "User", "Action", "Object", "Detail"], data=r
        )
