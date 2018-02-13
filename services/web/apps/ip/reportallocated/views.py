# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Allocated Blocks Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django Modules
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db.models import Q
# NOC Modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.validators import check_ipv4_prefix, check_ipv6_prefix, ValidationError
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.main.models.customfield import CustomField


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


class ReportAllocated(SimpleReport):
    title = _("Allocated Blocks")
    form = ReportForm

    def get_form(self):
        fc = super(ReportAllocated, self).get_form()
        self.customize_form(fc, "ip_prefix", search=True)
        return fc

    def get_data(self, vrf, afi, prefix, **kwargs):
        def get_row(p):
            r = [p.prefix, p.state.name, unicode(p.vc) if p.vc else ""]
            for f in cf:
                v = getattr(p, f.name)
                r += [v if v is not None else ""]
            r += [p.description, p]
            return r

        cf = CustomField.table_fields("ip_prefix")
        cfn = dict((f.name, f) for f in cf)
        # Prepare columns
        columns = [
            "Prefix",
            "State",
            "VC"
        ]
        for f in cf:
            columns += [f.label]
        columns += [
            "Description",
            TableColumn(_("Tags"), format="tags")
        ]
        # Prepare query
        q = Q()
        for k in kwargs:
            v = kwargs[k]
            if k in cfn and v is not None and v != "":
                q &= Q(**{str(k): v})
        #
        return self.from_dataset(
            title=_(
                "Allocated blocks in VRF %(vrf)s (IPv%(afi)s), %(prefix)s" % {
                    "vrf": vrf.name,
                    "afi": afi,
                    "prefix": prefix.prefix
                }
            ),
            columns=columns,
            data=[get_row(p) for p in prefix.children_set.filter(q).order_by("prefix")],
            enumerate=True
        )
