# ---------------------------------------------------------------------
# Failed Scripts Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms
from pymongo import ReadPreference

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, PredefinedReport, SectionRow
from noc.core.mongo.connection import get_db
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.sa.models.profile import GENERIC_PROFILE
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.resourcegroup import ResourceGroup
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
            status = ManagedObject.get_statuses(self.mo_ids)
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
            {
                "$project": {
                    "j_id": {"$concat": ["discovery-", "$jcls", "-", {"$substr": ["$key", 0, -1]}]},
                    "st": True,
                    "key": True,
                }
            },
            {
                "$lookup": {
                    "from": "noc.joblog",
                    "localField": "j_id",
                    "foreignField": "_id",
                    "as": "job",
                }
            },
            {"$project": {"job.problems": True, "st": True, "key": True}},
        ]
        if self.match:
            # @todo check match
            pipeline += [{"$match": self.match}]
        else:
            pipeline += [{"$match": {"job.problems": {"$exists": True, "$ne": {}}}}]
        return pipeline

    def __iter__(self):
        for p in self.mos_pools:
            r = (
                get_db()[self.coll_name % p.name]
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(self.pipelines.get(p.name, self.pipeline()))
            )
            for x in r:
                # @todo Append info for MO
                yield x


class ReportForm(forms.Form):
    pool = forms.ChoiceField(
        label=_("Managed Objects Pool"),
        required=False,
        choices=[*list(Pool.objects.order_by("name").scalar("id", "name")), (None, "-" * 9)],
    )
    obj_profile = forms.ModelChoiceField(
        label=_("Managed Objects Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.order_by("name"),
    )
    resource_group = forms.ChoiceField(
        label=_("Managed Objects Group (Selector)"),
        required=False,
        help_text="Group for choice",
        choices=[
            *list(ResourceGroup.objects.order_by("name").scalar("id", "name")),
            (None, "-" * 9),
        ],
    )
    avail_status = forms.BooleanField(label=_("Filter by Ping status"), required=False)
    profile_check_only = forms.BooleanField(label=_("Profile check only"), required=False)
    failed_scripts_only = forms.BooleanField(label=_("Failed discovery only"), required=False)
    filter_pending_links = forms.BooleanField(label=_("Filter Pending links"), required=False)
    filter_none_objects = forms.BooleanField(label=_("Filter None problems"), required=False)
    filter_view_other = forms.BooleanField(label=_("Show other problems"), required=False)


class ReportFilterApplication(SimpleReport):
    title = _("Discovery Problem")
    form = ReportForm

    predefined_reports = {
        pname: PredefinedReport(_("Problem Discovery (pool)") + f": {pname}", {"pool": str(pid)})
        for pid, pname in ([*list(Pool.objects.order_by("name").scalar("id", "name")), ("", "ALL")])
    }

    def get_data(
        self,
        request,
        pool=None,
        obj_profile=None,
        resource_group=None,
        avail_status=None,
        profile_check_only=None,
        failed_scripts_only=None,
        filter_pending_links=None,
        filter_none_objects=None,
        filter_view_other=None,
        **kwargs,
    ):
        data = []
        match = None
        code_map = {
            "1": "Unknown error",
            "10000": "Unspecified CLI error",
            "10005": "Connection refused",
            "10001": "Authentication failed",
            "10002": "No super command defined",
            "10003": "No super privileges",
            "10004": "SSH Protocol error",
        }

        if pool:
            pool = Pool.get_by_id(pool)
        else:
            pool = Pool.objects.filter()[0]
        data += [SectionRow(name="Report by %s" % pool.name)]
        if resource_group:
            resource_group = ResourceGroup.get_by_id(resource_group)
            mos = ManagedObject.objects.filter(
                effective_service_groups__overlap=ResourceGroup.get_nested_ids(resource_group)
            )
        else:
            mos = ManagedObject.objects.filter(pool=pool, is_managed=True)
        if not request.user.is_superuser:
            mos = mos.filter(administrative_domain__in=UserAccess.get_domains(request.user))
        if obj_profile:
            mos = mos.filter(object_profile=obj_profile)
        if filter_view_other:
            mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))
            mos = mos.filter(profile=Profile.objects.get(name=GENERIC_PROFILE)).exclude(
                object_profile__in=mnp_in
            )
        if profile_check_only:
            match = {
                "$or": [
                    {"job.problems.suggest_cli": {"$exists": True}},
                    {"job.problems.suggest_snmp": {"$exists": True}},
                    {"job.problems.profile.": {"$regex": "Cannot detect profile"}},
                    {"job.problems.version.": {"$regex": "Remote error code 1000[1234]"}},
                ]
            }
        elif failed_scripts_only:
            match = {
                "$and": [
                    {"job.problems": {"$exists": "true", "$ne": {}}},
                    {"job.problems.suggest_snmp": {"$exists": False}},
                    {"job.problems.suggest_cli": {"$exists": False}},
                ]
            }
        elif filter_view_other:
            match = {"job.problems.suggest_snmp": {"$exists": False}}
        rdp = ReportDiscoveryProblem(mos, avail_only=avail_status, match=match)
        exclude_method = []
        if filter_pending_links:
            exclude_method += ["lldp", "lacp", "cdp", "huawei_ndp"]
        for discovery in rdp:
            mo = ManagedObject.get_by_id(discovery["key"])
            for method in [x for x in discovery["job"][0]["problems"] if x not in exclude_method]:
                problem = discovery["job"][0]["problems"][method]
                if filter_none_objects and not problem:
                    continue
                if isinstance(problem, dict) and "" in problem:
                    problem = problem.get("", "")
                if "Remote error code" in problem:
                    problem = code_map.get(problem.split(" ")[-1], problem)
                if isinstance(problem, str):
                    problem = problem.replace("\n", " ").replace("\r", " ")
                data += [
                    (
                        mo.name,
                        mo.address,
                        mo.profile.name,
                        mo.administrative_domain.name,
                        _("Yes") if mo.get_status() else _("No"),
                        discovery["st"].strftime("%d.%m.%Y %H:%M") if "st" in discovery else "",
                        method,
                        problem,
                    )
                ]
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"),
                _("Address"),
                _("Profile"),
                _("Administrative Domain"),
                _("Avail"),
                _("Last successful discovery"),
                _("Discovery"),
                _("Error"),
            ],
            data=data,
        )
