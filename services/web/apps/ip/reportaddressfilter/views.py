# ---------------------------------------------------------------------
# ip.reportfilter
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.main.models.customfield import CustomField
from noc.ip.models.vrf import VRF
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from noc.sa.models.managedobject import ManagedObject
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Filter Address")

    def get_form(self):
        class RForm(forms.Form):
            vrf = forms.ModelChoiceField(
                label=_("VRF"), required=False, queryset=VRF.objects.order_by("name")
            )
            afi = forms.ChoiceField(
                label=_("Address Family"),
                required=False,
                choices=[("", "All"), ("4", _("IPv4")), ("6", _("IPv6"))],
            )
            managed_object = forms.CharField(label=_("Managed Object"), required=False)
            description = forms.CharField(label=_("Description"), required=False)
            fqdn = forms.CharField(label=_("FQDN"), required=False)
            name = forms.CharField(label=_("Name"), required=False)
            prefix = forms.CharField(label=_("Prefix"), required=False)

        self.customize_form(RForm, "ip_address", search=True)
        return RForm

    def get_data(self, request, **kwargs):
        def get_row(a):
            r = [
                a.vrf.name,
                a.prefix.prefix,
                a.address,
                a.state.name,
                smart_text(a.fqdn) if a.fqdn else "",
            ]
            for f in cf:
                v = getattr(a, f.name)
                r += [v if v is not None else ""]
            r += [a.description, a]
            return r

        def get_or_none(classmodel, **kwargs):
            try:
                return classmodel.objects.filter(**kwargs)
            except classmodel.DoesNotExist:
                return None

        q = {}
        for k in kwargs:
            v = kwargs[k]
            if v:
                if k in ["description", "fqdn", "name"]:
                    q[k + "__icontains"] = v
                elif k == "prefix":
                    q[k + "__in"] = get_or_none(Prefix, prefix=v)
                elif k == "managed_object":
                    q[k + "__in"] = get_or_none(ManagedObject, name=v)
                else:
                    q[k] = v
        columns = ["VRF", "Prefix", "Address", "State", "FQDN"]
        cf = CustomField.table_fields("ip_address")
        for f in cf:
            if f.type == "bool":
                columns += [TableColumn(f.label, format="bool")]
            else:
                columns += [f.label]
        columns += ["Description", TableColumn(_("Tags"), format="tags")]

        data = [
            get_row(a)
            for a in Address.objects.filter(**q).order_by("vrf__name", "address").select_related()
        ]
        return self.from_dataset(title=self.title, columns=columns, data=data)
