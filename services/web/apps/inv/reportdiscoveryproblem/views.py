# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportdiscovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
from django import forms
## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.objectuplink import ObjectUplink
from noc.main.models.pool import Pool
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pools"),
        required=True,
        queryset=Pool.objects.order_by("name"))


class ReportDiscoveryProblemApplication(SimpleReport):
    title = _("Discovery Problems")
    form = ReportForm

    def get_data(self, request, pool, **kwargs):
        problems = {}  # id -> problem
        # Get all managed objects
        mos = dict(
            (mo.id, mo)
            for mo in ManagedObject.objects.filter(is_managed=True, pool=pool)
        )
        if not request.user.is_superuser:
            mos = dict(
                (mo.id, mo)
                for mo in ManagedObject.objects.filter(is_managed=True, pool=pool,
                                                       administrative_domain__in=UserAccess.get_domains(request.user))
            )

        mos_set = set(mos)
        # Get all managed objects with Generic.Host profiles
        for mo in mos:
            if mos[mo].profile_name == "Generic.Host":
                problems[mo] = _("Profile check failed")
        # Get all managed objects without interfaces
        if_mo = dict(
            (x["_id"], x.get("managed_object"))
            for x in Interface._get_collection().find(
                {},
                {"_id": 1, "managed_object": 1}
            )
        )
        for mo in (mos_set - set(problems) - set(if_mo.itervalues())):
            problems[mo] = _("No interfaces")
        # Get all managed objects without links
        linked_mos = set()
        for d in Link._get_collection().find({}):
            for i in d["interfaces"]:
                linked_mos.add(if_mo.get(i))
        for mo in (mos_set - set(problems) - linked_mos):
            problems[mo] = _("No links")
        # Get all managed objects without uplinks
        uplinks = {}
        for d in ObjectUplink._get_collection().find():
            nu = len(d.get("uplinks", []))
            if nu:
                uplinks[d["_id"]] = nu
        for mo in (mos_set - set(problems) - set(uplinks)):
            problems[mo] = _("No uplinks")
        #
        data = []
        for mo_id in problems:
            if mo_id not in mos:
                continue
            mo = mos[mo_id]
            data += [[
                mo.name,
                mo.address,
                mo.profile_name,
                mo.platform,
                mo.segment.name if mo.segment else "",
                problems[mo_id]
            ]]
        data = sorted(data)
        return self.from_dataset(
            title=self.title,
            columns=[
                "Name",
                "Address",
                "Profile",
                "Platform",
                "Segment",
                "Problem"
            ],
            data=data,
            enumerate=True
        )
