# ---------------------------------------------------------------------
# inv.reportdiscoverycaps
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.base.simplereport import SimpleReport
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportDiscoveryCapsApplication(SimpleReport):
    title = _("Discovery Object Caps")

    def get_form(self):
        class ReportForm(forms.Form):
            pool = forms.ChoiceField(
                label=_("Managed Objects Pool"),
                required=True,
                choices=[
                    *list(Pool.objects.order_by("name").scalar("id", "name")),
                    (None, "-" * 9),
                ],
            )
            obj_profile = forms.ModelChoiceField(
                label=_("Managed Objects Profile"),
                required=False,
                queryset=ManagedObjectProfile.objects.order_by("name"),
            )

        return ReportForm

    def get_data(self, request, pool=None, obj_profile=None, **kwargs):
        data = []
        if pool:
            pool = Pool.get_by_id(pool)
        else:
            pool = Pool.get_by_name("default")
        # Get all managed objects
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)
        if not request.user.is_superuser:
            mos = ManagedObject.objects.filter(
                is_managed=True,
                pool=pool,
                administrative_domain__in=UserAccess.get_domains(request.user),
            )
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)
        columns = (_("Managed Object"), _("Address"), _("Object"), _("Capabilities"))
        for mo in mos:
            mo.get_caps()
            data += [(mo.name, mo.address, _("Main"), ";".join(mo.get_caps()))]
            for i in Interface.objects.filter(managed_object=mo):
                if i.type == "SVI":
                    continue
                data += [(mo.name, mo.address, i.name, ";".join(i.enabled_protocols))]
        return self.from_dataset(title=self.title, columns=columns, data=data)
