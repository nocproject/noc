# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python Modules
import math
# Django Modules
from django.utils.translation import ugettext_lazy as _
from django import forms
# NOC Modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.ip.models import VRF, Prefix
from noc.lib.validators import *
from noc.lib.ip import *


class ReportForm(forms.Form):
    vrf = forms.ModelChoiceField(
        label=_("VRF"),
        queryset=VRF.objects.filter(
            state__is_provisioned=True).order_by("name"))
    afi = forms.ChoiceField(label=_("Address Family"),
                            choices=[("4", _("IPv4"))])
    prefix = forms.CharField(label=_("Prefix"))

    def clean_prefix(self):
        vrf = self.cleaned_data["vrf"]
        afi = self.cleaned_data["afi"]
        prefix = self.cleaned_data.get("prefix", "").strip()
        if afi == "4":
            check_ipv4_prefix(prefix)
        elif afi == "6":
            check_ipv6_prefix(prefix)
        try:
            return Prefix.objects.get(vrf=vrf, afi=afi, prefix=prefix)
        except Prefix.DoesNotExist:
            raise ValidationError(_("Prefix not found"))


class ReportSummary(SimpleReport):
    title = "Block Summary"
    form = ReportForm

    def get_data(self, vrf, afi, prefix, **kwargs):
        p = IP.prefix(prefix.prefix)
        allocated = [IP.prefix(a.prefix) for a in prefix.children_set.all()]
        if afi == "4":
            allocated_30 = [a for a in allocated if a.mask == 30]
        free = list(p.iter_free(allocated))
        if afi == "4":
            allocated_size = sum([a.size for a in allocated])
            allocated_30_size = sum([a.size for a in allocated_30])
            free_size = sum([a.size for a in free])
            total = p.size
            data = [
                ("Allocated addresses", allocated_size,
                 float(allocated_size) * 100 / float(total)),
                (".... in /30", allocated_30_size,
                 float(allocated_30_size) * 100 / float(total)),
                ("Free addresses", free_size,
                 float(free_size) * 100 / float(total)),
                ("Total addresses", total, 1.0)
            ]
            a_s = len(allocated)
            if a_s:
                avg_allocated_size = allocated_size / a_s
                avg_allocated_mask = 32 - int(
                    math.ceil(math.log(avg_allocated_size, 2)))
                data += [
                    ("Average allocated block", avg_allocated_size, ""),
                    ("Average allocated mask", avg_allocated_mask, "")
                ]
            return self.from_dataset(
                title=_("Summary for VRF %(vrf)s (IPv%(afi)s): %(prefix)s") % {
                    "vrf": vrf.name,
                    "afi": afi,
                    "prefix": p.prefix
                },
                columns=["",
                         TableColumn(_("Size"),
                                     format="numeric", align="right"),
                         TableColumn(_("%"), format="percent", align="right")],
                data=data)

