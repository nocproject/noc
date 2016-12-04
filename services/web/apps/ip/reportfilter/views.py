# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.reportfilter
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db.models import Q
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.main.models.customfield import CustomField
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.peer.models import AS


class ReportFilterApplication(SimpleReport):
    title = _("Filter")

    def get_form(self):
        class RForm(forms.Form):
            vrf = forms.ModelChoiceField(
                label=_("VRF"),
                required=False,
                queryset=VRF.objects.order_by("name"))
            afi = forms.ChoiceField(
                label=_("Address Family"),
                required=False,
                choices=[
                    ("", "All"),
                    ("4", _("IPv4")),
                    ("6", _("IPv6"))])
            asn = forms.ModelChoiceField(
                label=_("AS Number"),
                required=False,
                queryset=AS.objects.order_by("asn")
            )
            description = forms.CharField(
                label=_("Description"),
                required = False
            )

        self.customize_form(RForm, "ip_prefix", search=True)
        return RForm

    def get_data(self, **kwargs):
        def get_row(p):
            r = [p.vrf.name, p.prefix, p.state.name, unicode(p.asn),
                unicode(p.vc) if p.vc else ""]
            for f in cf:
                v = getattr(p, f.name)
                r += [v if v is not None else ""]
            r += [p.description, p]
            return r

        q = {}
        for k in kwargs:
            v = kwargs[k]
            if v:
                if k == "description":
                    q[k + "__icontains"] = v
                else:
                    q[k] = v
        columns = ["VRF", "Prefix", "State", "AS", "VC"]
        cf = CustomField.table_fields("ip_prefix")
        for f in cf:
            if f.type == "bool":
                columns += [TableColumn(f.label, format="bool")]
            else:
                columns += [f.label]
        columns += [
            "Description",
            TableColumn(_("Tags"), format="tags")
        ]

        data = [get_row(p)
                for p in Prefix.objects.filter(**q)\
                    .exclude(prefix="0.0.0.0/0")\
                    .exclude(prefix="::/0")\
                    .order_by("vrf__name", "prefix").select_related()]
        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data
        )
