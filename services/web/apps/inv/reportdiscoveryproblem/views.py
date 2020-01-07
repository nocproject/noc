# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from django import forms

# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobject import ManagedObjectProfile
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.objectdata import ObjectData
from noc.main.models.pool import Pool
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.core.profile.loader import GENERIC_PROFILE


class ReportDiscoveryTopologyProblemApplication(SimpleReport):
    title = _("Discovery Topology Problems")

    def get_form(self):
        class ReportForm(forms.Form):
            pool = forms.ChoiceField(
                label=_("Managed Objects Pools"),
                required=True,
                choices=list(Pool.objects.order_by("name").scalar("id", "name"))
                + [(None, "-" * 9)],
            )
            obj_profile = forms.ModelChoiceField(
                label=_("Managed Objects Profile"),
                required=False,
                queryset=ManagedObjectProfile.objects.order_by("name"),
            )

        return ReportForm

    def get_data(self, request, pool=None, obj_profile=None, **kwargs):
        problems = {}  # id -> problem

        mos = ManagedObject.objects.filter(is_managed=True, pool=pool)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            # Get all managed objects
            mos = mos.filter(object_profile=obj_profile)
        mos = {
            mo[0]: (mo[1], mo[2], Profile.get_by_id(mo[3]), mo[4], mo[5])
            for mo in mos.values_list("id", "name", "address", "profile", "platform", "segment")
        }
        mos_set = set(mos)
        # Get all managed objects with generic profile
        for mo in mos:
            if mos[mo][2] == GENERIC_PROFILE:
                problems[mo] = _("Profile check failed")
        # Get all managed objects without interfaces
        if_mo = dict(
            (x["_id"], x.get("managed_object"))
            for x in Interface._get_collection().find({}, {"_id": 1, "managed_object": 1})
        )
        for mo in mos_set - set(problems) - set(six.itervalues(if_mo)):
            problems[mo] = _("No interfaces")
        # Get all managed objects without links
        linked_mos = set()
        for d in Link._get_collection().find({}):
            for i in d["interfaces"]:
                linked_mos.add(if_mo.get(i))
        for mo in mos_set - set(problems) - linked_mos:
            problems[mo] = _("No links")
        # Get all managed objects without uplinks
        uplinks = {}
        for d in ObjectData._get_collection().find():
            nu = len(d.get("uplinks", []))
            if nu:
                uplinks[d["_id"]] = nu
        for mo in mos_set - set(problems) - set(uplinks):
            problems[mo] = _("No uplinks")
        #
        data = []
        for mo_id in problems:
            if mo_id not in mos:
                continue
            name, address, profile, platform, segment = mos[mo_id]
            data += [
                [
                    name,
                    address,
                    profile.name,
                    Platform.get_by_id(platform).name if platform else "",
                    NetworkSegment.get_by_id(segment).name if segment else "",
                    problems[mo_id],
                ]
            ]
        data = sorted(data)
        return self.from_dataset(
            title=self.title,
            columns=["Name", "Address", "Profile", "Platform", "Segment", "Problem"],
            data=data,
            enumerate=True,
        )
