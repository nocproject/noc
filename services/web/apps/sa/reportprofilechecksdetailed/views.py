# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Failed Scripts Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, PredefinedReport
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.profile import Profile
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.services.web.apps.sa.reportobjectdetail.views import ReportObjectsHostname
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _
from noc.core.profile.loader import GENERIC_PROFILE


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pool"),
        required=False,
        help_text="Pool for choice",
        queryset=Pool.objects.order_by("name"))
    selector = forms.ModelChoiceField(
        label=_("Managed Objects Selector"),
        required=False,
        help_text="Selector for choice",
        queryset=ManagedObjectSelector.objects.order_by("name"))


class ReportFilterApplication(SimpleReport):
    title = _("Failed Discovery")
    form = ReportForm
    try:
        default_pool = Pool.objects.get(name="default")
    except:
        default_pool = Pool.objects.all()[0]
    predefined_reports = {
        "default": PredefinedReport(
            _("Failed Discovery (default)"), {
                "pool": default_pool
            }
        )
    }

    def get_data(self, request, pool=None,
                 selector=None, avail_status=None, **kwargs):
        data = []

        mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))
        if pool:
            base = ManagedObject.objects.filter(pool=pool)
            data += [SectionRow(name=pool.name)]
        elif selector:
            base = ManagedObject.objects.filter(selector.Q)
            data += [SectionRow(name=selector.name)]
        else:
            return self.from_dataset(
                title=self.title,
                columns=[
                    _("Managed Object"), _("Address"), _("Profile"), _("Hostname"),
                    _("Auth Profile"), _("Username"), _("SNMP Community"),
                    _("Avail"), _("Error")
                ],
                data=data)

        is_managed = base.filter(is_managed=True).exclude(object_profile__in=mnp_in)
        is_not_man = base.filter(is_managed=False)
        is_not_resp = base.filter(is_managed=True, object_profile__in=mnp_in)
        if not request.user.is_superuser:
            is_managed = is_managed.filter(administrative_domain__in=UserAccess.get_domains(request.user))
            is_not_man = is_not_man.filter(administrative_domain__in=UserAccess.get_domains(request.user))
            is_not_resp = is_not_resp.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        is_managed_not_generic = is_managed.exclude(profile=Profile.get_by_name(GENERIC_PROFILE))
        is_managed_undef = is_managed.filter(profile=Profile.get_by_name(GENERIC_PROFILE))
        is_managed_undef_in = list(is_managed_undef.values_list("id", flat=True))
        is_managed_not_generic_in = list(is_managed_not_generic.values_list("id", flat=True))

        # is_alive = [s.id for s in is_managed if s.get_status()]
        is_alive_id = get_db()["noc.cache.object_status"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find({"object": {"$in": is_managed_undef_in},
                                                                      "status": True},
                                                                     {"_id": 1, "object": 1})
        is_alive_id_ng = get_db()["noc.cache.object_status"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find({"object": {"$in": is_managed_not_generic_in},
                                                                      "status": True},
                                                                     {"_id": 1, "object": 1})
        is_not_alived_c = get_db()["noc.cache.object_status"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find({"object": {"$in": is_managed_undef_in},
                                                                      "status": False},
                                                                     {"_id": 1, "object": 1})
        is_managed_alive_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                               m["object"] for m in is_alive_id]
        is_managed_ng_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                            m["object"] for m in is_alive_id_ng]
        bad_snmp_cred = get_db()["noc.joblog"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).find(
            {"problems.suggest_snmp.": "Failed to guess SNMP community",
             "_id": {"$in": is_managed_alive_in}})
        bad_cli_cred = get_db()["noc.joblog"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).find(
            {"problems.suggest_cli.": "Failed to guess CLI credentials",
             "_id": {"$in": is_managed_ng_in}})
        mos_id = list(is_managed.values_list("id", flat=True))
        mo_hostname = ReportObjectsHostname(mo_ids=mos_id, use_facts=True)
        for b in is_not_alived_c:
            mo = ManagedObject.get_by_id(b["object"])
            data += [(
                mo.name,
                mo.address,
                mo.profile.name,
                mo.administrative_domain.name,
                mo_hostname[mo.id],
                mo.auth_profile if mo.auth_profile else "",
                mo.auth_profile.user if mo.auth_profile else mo.user,
                mo.auth_profile.snmp_ro if mo.auth_profile else mo.snmp_ro,
                _("No"),
                "Not Available"
            )]

        for b in bad_snmp_cred:
            mo = ManagedObject.get_by_id(int(b["_id"].split("-")[-1]))
            data += [(
                mo.name,
                mo.address,
                mo.administrative_domain.name,
                mo.profile.name,
                mo_hostname[mo.id],
                mo.auth_profile if mo.auth_profile else "",
                mo.auth_profile.user if mo.auth_profile else mo.user,
                mo.auth_profile.snmp_ro if mo.auth_profile else mo.snmp_ro,
                _("Yes") if mo.get_status() else _("No"),
                "Failed to guess SNMP community"
            )]
        for b in bad_cli_cred:
            mo = ManagedObject.get_by_id(int(b["_id"].split("-")[-1]))
            data += [(
                mo.name,
                mo.address,
                mo.administrative_domain.name,
                mo.profile.name,
                mo_hostname[mo.id],
                mo.auth_profile if mo.auth_profile else "",
                mo.auth_profile.user if mo.auth_profile else mo.user,
                mo.auth_profile.snmp_ro if mo.auth_profile else mo.snmp_ro,
                _("Yes"),
                "Failed to guess CLI credentials"
            )]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Administrative Domain"), _("Profile"), _("Hostname"),
                _("Auth Profile"), _("Username"), _("SNMP Community"),
                _("Avail"), _("Error")
            ],
            data=data)
