# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.objectdata import ObjectData
from noc.main.models.pool import Pool
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.core.profile.loader import GENERIC_PROFILE


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pools"),
        required=True,
        queryset=Pool.objects.order_by("name"))
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))


class ReportDiscoveryTopologyProblemApplication(SimpleReport):
    title = _("Discovery Topology Problems")
    form = ReportForm

    def get_data(self, request, pool, obj_profile=None, **kwargs):
        problems = {}  # id -> problem

        if not obj_profile:
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
        else:
            # Get all managed objects
            mos = dict(
                (mo.id, mo)
                for mo in ManagedObject.objects.filter(is_managed=True, pool=pool, object_profile=obj_profile)
            )
            if not request.user.is_superuser:
                mos = dict(
                    (mo.id, mo)
                    for mo in ManagedObject.objects.filter(is_managed=True, pool=pool, object_profile=obj_profile,
                                                           administrative_domain__in=UserAccess.get_domains(request.user))
                )

        mos_set = set(mos)
        # Get all managed objects with generic profile
        for mo in mos:
            if mos[mo].profile.name == GENERIC_PROFILE:
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
        for d in ObjectData._get_collection().find():
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
                mo.profile.name,
                mo.platform.name if mo.platform else "",
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
