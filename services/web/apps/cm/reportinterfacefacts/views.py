# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface Facts Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport, PredefinedReport
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.cm.models.objectfact import ObjectFact
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pool"),
        required=False,
        queryset=Pool.objects.order_by("name"))
    int_profile = forms.ModelChoiceField(
        label=_("Interface Profile"),
        required=True,
        queryset=InterfaceProfile.objects.order_by("name"))
    mop = forms.ModelChoiceField(
        label=_("Managed Object Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))
    # int_fact = forms.ModelChoiceField(
    #    label=_("Check Facts"),
    #    required=False,
    #    queryset=ManagedObjectProfile.objects.order_by("name"))


class ReportFilterApplication(SimpleReport):
    title = _("Check Interface Facts")
    form = ReportForm
    try:
        default_pool = Pool.objects.get(name="default")
    except:
        default_pool = Pool.objects.all()[0]
    predefined_reports = {
        "default": PredefinedReport(
            _("Check Interface Facts (default)"), {
                "pool": default_pool
            }
        )
    }

    def get_data(self, request, pool=None, int_profile=None,
                 mop=None, avail_status=None, **kwargs):
        data = []
        mos = ManagedObject.objects.filter(is_managed=True)

        # % fixme remove.
        if not pool and request.user.is_superuser:
            pool = Pool.get_by_name("STAGEMO")
        if pool:
            mos = mos.filter(pool=pool)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if mop:
            mos = mos.filter(object_profile=mop)
        mos_ids = mos.values_list("id", flat=True)

        iface = Interface.objects.filter(managed_object__in=mos,
                                         profile=int_profile,
                                         type="physical").values_list("managed_object", "name")
        res = []
        n = 0
        # Interface._get_collection()
        while mos_ids[(0 + n):(10000 + n)]:
            mos_ids_f = mos_ids[(0 + n):(10000 + n)]
            s_iface = set(["%d.%s" % (mo.id, name) for mo, name in iface])
            of = ObjectFact.objects.filter(object__in=mos_ids_f,
                                           cls="subinterface", attrs__traffic_control_broadcast=False)
            a_f = set([".".join((str(o.object.id), o.attrs["name"])) for o in of])
            res.extend(a_f.intersection(s_iface))
            n += 10000
        for s in res:
            mo, iface = s.split(".")
            mo = ManagedObject.get_by_id(mo)
            data += [
                (
                    mo.name,
                    mo.address,
                    mo.profile_name,
                    iface
                )
            ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("SA Profile"), _("Interface")
            ],
            data=data)
