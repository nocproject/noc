# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.reportdiscoverycaps
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from django import forms
from noc.core.translation import ugettext as _
from noc.inv.models.interface import Interface
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.useraccess import UserAccess


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pool"),
        required=True,
        queryset=Pool.objects.order_by("name"))
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))


class ReportDiscoveryCapsApplication(SimpleReport):
    title = _("Discovery Object Caps")
    form = ReportForm

    def get_data(self, request, pool="default", obj_profile=None, **kwargs):
        problems = {}  # id -> problem
        data = []
        # Get all managed objects
        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)
        if not request.user.is_superuser:
            mos = ManagedObject.objects.filter(is_managed=True, pool=pool,
                                               administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)
        columns = (_("Managed Object"), _("Address"), _("Object"), _("Capabilities"))
        for mo in mos:
            mo.get_caps()
            data += [(
                mo.name,
                mo.address,
                _("Main"),
                ";".join(mo.get_caps())
            )]
            for i in Interface.objects.filter(managed_object=mo):
                if i.type == "SVI":
                    continue
                data += [(
                    mo.name,
                    mo.address,
                    i.name,
                    ";".join(i.enabled_protocols)
                )]

        return self.from_dataset(
            title=self.title,
            columns=columns,
            data=data
        )
