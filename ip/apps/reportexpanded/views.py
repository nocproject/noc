# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Expanded Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django Modules
from django.utils.translation import ugettext_lazy as _
from django import forms
## NOC Modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.ip.models import VRF, Prefix
from noc.lib.validators import *


class ReportForm(forms.Form):
    """
    Report form
    """
    vrf = forms.ModelChoiceField(
        label=_("VRF"),
        queryset=VRF.objects.filter(
            state__is_provisioned=True).order_by("name"))
    afi = forms.ChoiceField(label=_("Address Family"),
                            choices=[("4", _("IPv4")), ("6", _("IPv6"))])
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


class ExpandedReport(SimpleReport):
    form = ReportForm
    title = "All Allocated Blocks"

    def get_data(self, vrf, afi, prefix, **kwargs):
        def get_info(prefix, level=0):
            s = "----" * level
            data = [[s + prefix.prefix, unicode(prefix.vc) if prefix.vc else "",
                     prefix.description, prefix]]
            for c in prefix.children_set.order_by("prefix"):
                data += get_info(c, level + 1)
            return data

        data = get_info(prefix)
        return self.from_dataset(title=_(
            "All allocated blocks in VRF %(vrf)s (IPv%(afi)s), %(prefix)s" % {
                "vrf": vrf.name,
                "afi": afi,
                "prefix": prefix.prefix
            }),
            columns=[_("Prefix"), _("VC"), _("Description"),
                     TableColumn(_("Tags"), format="tags")],
            data=data, enumerate=True)
