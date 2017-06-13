# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# Failed Scripts Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow, PredefinedReport, TableColumn
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.services.web.apps.sa.reportobjectdetail.views import ReportObjectsHostname
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pool"),
        required=True,
        queryset=Pool.objects.order_by("name"))


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

    def get_data(self, request, pool=Pool.objects.filter()[0], avail_status=None, **kwargs):
        data = []

        data += [SectionRow(name=pool.name)]

        mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))

        is_managed = ManagedObject.objects.filter(is_managed=True, pool=pool).exclude(object_profile__in=mnp_in)
        is_not_man = ManagedObject.objects.filter(is_managed=False, pool=pool)
        is_not_resp = ManagedObject.objects.filter(is_managed=True, pool=pool, object_profile__in=mnp_in)
        if not request.user.is_superuser:
            is_managed = is_managed.filter(administrative_domain__in=UserAccess.get_domains(request.user))
            is_not_man = is_not_man.filter(administrative_domain__in=UserAccess.get_domains(request.user))
            is_not_resp = is_not_resp.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        is_managed_not_generic = is_managed.exclude(profile_name="Generic.Host")
        is_managed_undef = is_managed.filter(profile_name="Generic.Host")
        is_managed_undef_in = list(is_managed_undef.values_list("id", flat=True))
        is_managed_not_generic_in = list(is_managed_not_generic.values_list("id", flat=True))

        # is_alive = [s.id for s in is_managed if s.get_status()]
        is_alive_id = get_db()["noc.cache.object_status"].find({"object": {"$in": is_managed_undef_in},
                                                                "status": True},
                                                               {"_id": 1, "object": 1},
                                                               read_preference=ReadPreference.SECONDARY_PREFERRED)
        is_alive_id_ng = get_db()["noc.cache.object_status"].find({"object": {"$in": is_managed_not_generic_in},
                                                                   "status": True},
                                                                  {"_id": 1, "object": 1},
                                                                  read_preference=ReadPreference.SECONDARY_PREFERRED)
        is_not_alived_c = get_db()["noc.cache.object_status"].find({"object": {"$in": is_managed_undef_in},
                                                                    "status": False},
                                                                   {"_id": 1, "object": 1},
                                                                   read_preference=ReadPreference.SECONDARY_PREFERRED)
        is_managed_alive_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                               m["object"] for m in is_alive_id]
        is_managed_ng_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                            m["object"] for m in is_alive_id_ng]
        bad_snmp_cred = get_db()["noc.joblog"].find({"problems.suggest_snmp": "Failed to guess SNMP community",
                                                     "_id": {"$in": is_managed_alive_in}},
                                                    read_preference=ReadPreference.SECONDARY_PREFERRED)
        bad_cli_cred = get_db()["noc.joblog"].find({"problems.suggest_cli": "Failed to guess CLI credentials",
                                                    "_id": {"$in": is_managed_ng_in}},
                                                   read_preference=ReadPreference.SECONDARY_PREFERRED)
        mos_id = list(is_managed.values_list("id", flat=True))
        mo_hostname = ReportObjectsHostname(mo_ids=mos_id, use_facts=True)
        for b in is_not_alived_c:
            mo = ManagedObject.get_by_id(b["object"])
            data += [(
                mo.name,
                mo.address,
                mo.profile_name,
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
                mo.profile_name,
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
                mo.profile_name,
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
                _("Managed Object"), _("Address"), _("Profile"), _("Hostname"),
                _("Auth Profile"), _("Username"), _("SNMP Community"),
                _("Avail"), _("Error")
            ],
            data=data)
