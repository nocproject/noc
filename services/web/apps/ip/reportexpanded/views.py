# ---------------------------------------------------------------------
# Expanded Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party Modules
from django import forms

# NOC Modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.main.models.customfield import CustomField
from noc.core.validators import check_ipv6_prefix, check_ipv4_prefix, ValidationError
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _
from noc.vc.models.vlan import VLAN


class ReportForm(forms.Form):
    """
    Report form
    """

    vrf = forms.ModelChoiceField(label=_("VRF"), queryset=VRF.objects.all().order_by("name"))
    afi = forms.ChoiceField(label=_("Address Family"), choices=[("4", _("IPv4")), ("6", _("IPv6"))])
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
        def get_row(p, level=0):
            vlan = VLAN.get_by_id(p.vlan.id) if p.vlan else None
            s = "--" * level
            r = [s + p.prefix, p.state.name, smart_text(vlan) if vlan else ""]
            for f in cf:
                v = getattr(p, f.name)
                r += [v if v is not None else ""]
            r += [p.description, p]
            return r

        def get_info(prefix, level=0):
            data = [get_row(prefix, level)]
            for c in prefix.children_set.order_by("prefix"):
                data += get_info(c, level + 1)
            return data

        cf = CustomField.table_fields("ip_prefix")
        # Prepare columns
        columns = ["Prefix", "State", "VLAN"]
        for f in cf:
            columns += [f.label]
        columns += ["Description", TableColumn(_("Tags"), format="tags")]
        data = get_info(prefix)
        return self.from_dataset(
            title=_(
                "All allocated blocks in VRF %(vrf)s (IPv%(afi)s), %(prefix)s"
                % {"vrf": vrf.name, "afi": afi, "prefix": prefix.prefix}
            ),
            columns=columns,
            data=data,
            enumerate=True,
        )
