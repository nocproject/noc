# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Free Blocks Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django import forms
# NOC Modules
from noc.lib.app.simplereport import SimpleReport
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.lib.validators import check_ipv4_prefix, check_ipv6_prefix, ValidationError
from noc.core.ip import IP


class ReportForm(forms.Form):
    vrf = forms.ModelChoiceField(
        label=_("VRF"),
        queryset=VRF.objects.filter(
            state__is_provisioned=True).order_by("name")
    )
    afi = forms.ChoiceField(label=_("Address Family"),
                            choices=[("4", _("IPv4")), ("6", _("IPv6"))])
    prefix = forms.CharField(label=_("Prefix"))

    def clean_prefix(self):
        vrf = self.cleaned_data.get("vrf")
        if not vrf:
            raise ValidationError(_("VRF Required"))
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


class FreeBlocksReport(SimpleReport):
    title = _("Free Blocks")
    form = ReportForm

    def get_data(self, vrf, afi, prefix, **kwargs):
        p = IP.prefix(prefix.prefix)
        return self.from_dataset(
            title=_(
                "Free blocks in VRF %(vrf)s (IPv%(afi)s), %(prefix)s" % {
                    "vrf": vrf.name,
                    "afi": afi,
                    "prefix": prefix.prefix
                }
            ),
            columns=["Free Blocks"],
            data=[
                [unicode(f)] for f in p.iter_free([
                    IP.prefix(c.prefix)
                    for c in prefix.children_set.all()
                ])
            ]
        )
