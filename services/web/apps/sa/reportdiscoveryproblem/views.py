# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------
# Failed Discovery Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
from itertools import ifilterfalse
# Third-party modules
from django import forms
# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport, SectionRow
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.objectstatus import ObjectStatus
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportDiscoveryProblem(object):
    """Report for MO links detail"""
    def __init__(self, mos, avail_only=False, match=None):
        """

        :param mos:
        :type mos: ManagedObject.objects.filter()
        """
        self.mo_ids = list(mos.values_list("id", flat=True))
        if avail_only:
            status = ObjectStatus.get_statuses(self.mo_ids)
            self.mo_ids = [s for s in status if status[s]]
        self.mos_pools = [Pool.get_by_id(p) for p in set(mos.values_list("pool", flat=True))]
        self.coll_name = "noc.schedules.discovery.%s"
        # @todo Good way for pipelines fill
        self.pipelines = {}
        self.match = match

    def pipeline(self, match=None):
        """
        Generate pipeline for request
        :param match: Match filter
        :type match: dict
        :return:
        :rtype: list
        """
        discovery = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        pipeline = [
            {"$match": {"key": {"$in": self.mo_ids}, "jcls": discovery}},
            {"$project": {
                "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                "st": True,
                "key": True}},
            {"$lookup": {"from": "noc.joblog", "localField": "j_id", "foreignField": "_id", "as": "job"}},
            {"$project": {"job.problems": True, "st": True, "key": True}}]
        if self.match:
            # @todo check match
            pipeline += [{"$match": self.match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {  }}}}]
        return pipeline

    def __iter__(self):
        for p in self.mos_pools:
            r = get_db()[self.coll_name % p.name].aggregate(self.pipelines.get(p.name, self.pipeline()),
                                                            read_preference=ReadPreference.SECONDARY_PREFERRED)
            for x in r["result"]:
                # @todo Append info for MO
                yield x


class ReportForm(forms.Form):
    pool = forms.ModelChoiceField(
        label=_("Managed Objects Pool"),
        required=False,
        queryset=Pool.objects.order_by("name"))
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"))
    selector = forms.ModelChoiceField(
        label=_("Managed Objects Selector"),
        required=False,
        queryset=ManagedObjectSelector.objects.order_by("name"))
    avail_status = forms.BooleanField(
        label=_("Filter by Ping status"),
        required=False
    )
    profile_check_only = forms.BooleanField(
        label=_("Profile check only"),
        required=False
    )
    failed_scripts_only = forms.BooleanField(
        label=_("Failed discovery only"),
        required=False
    )
    filter_pending_links = forms.BooleanField(
        label=_("Filter Pending links"),
        required=False
    )
    filter_none_objects = forms.BooleanField(
        label=_("Filter None problems"),
        required=False
    )
    filter_view_other = forms.BooleanField(
        label=_("Show other problems"),
        required=False
    )


class ReportFilterApplication(SimpleReport):
    title = _("Discovery Problem")
    form = ReportForm
    try:
        default_selector = ManagedObjectSelector.resolve_expression("@Problem Discovery Report")
    except ManagedObjectSelector.DoesNotExist:
        default_selector = None
    predefined_reports = {
        "default": PredefinedReport(
            _("Problem Discovery 2(default)"), {
                "selector": default_selector
            }
        )
    }

    def get_data(self, request, pool=None, obj_profile=None, selector=None,
                 avail_status=None, profile_check_only=None,
                 failed_scripts_only=None, filter_pending_links=None,
                 filter_none_objects=None, filter_view_other=None,
                 **kwargs):
        data = []
        match = None
        code_map = {
            "1": "Unknown error",
            "10000": "Unspecified CLI error",
            "10005": "Connection refused",
            "10001": "Authentication failed",
            "10002": "No super command defined",
            "10003": "No super privileges",
            "10004": "SSH Protocol error"
        }

        if not pool:
            pool = Pool.objects.filter()[0]
        data += [SectionRow(name="Report by %s" % pool.name)]
        if selector:
            mos = ManagedObject.objects.filter(selector.Q)
        else:
            mos = ManagedObject.objects.filter(pool=pool, is_managed=True)

        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)
        if filter_view_other:
            mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))
            mos = mos.filter(profile_name="Generic.Host").exclude(object_profile__in=mnp_in)

        if profile_check_only:
            match = {"$or": [{"job.problems.suggest_cli": {"$exists": True}},
                             {"job.problems.suggest_snmp": {"$exists": True}}]}

        elif failed_scripts_only:
            match = {"$and": [
                {"job.problems": {"$exists": "true", "$ne": {}}},
                {"job.problems.suggest_snmp": {"$exists": False}},
                {"job.problems.suggest_cli": {"$exists": False}}]}
        elif filter_view_other:
            match = {"job.problems.suggest_snmp": {"$exists": False}}

        rdp = ReportDiscoveryProblem(mos, avail_only=avail_status, match=match)
        exclude_method = []
        if filter_pending_links:
            exclude_method += ["lldp", "lacp", "cdp"]

        for discovery in rdp:
                mo = ManagedObject.get_by_id(discovery["key"])
                for method in ifilterfalse(lambda x: x in exclude_method, discovery["job"][0]["problems"]):
                    problem = discovery["job"][0]["problems"][method]
                    if filter_none_objects and not problem:
                        continue
                    if isinstance(problem, dict) and "" in problem:
                        problem = problem.get("", "")
                    if "Remote error code" in problem:
                        problem = code_map.get(problem.split(" ")[-1], problem)
                    if isinstance(problem, six.string_types):
                        problem = problem.replace("\n", " ").replace("\r", " ")

                    data += [
                        (
                            mo.name,
                            mo.address,
                            mo.profile_name,
                            _("Yes") if mo.get_status() else _("No"),
                            discovery["st"].strftime("%d.%m.%Y %H:%M") if "st" in discovery else "",
                            method,
                            problem
                        )
                    ]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"), _("Profile"),
                _("Avail"), _("Last successful discovery"),
                _("Discovery"), _("Error")
            ],
            data=data)
