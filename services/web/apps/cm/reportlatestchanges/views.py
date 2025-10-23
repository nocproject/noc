# ---------------------------------------------------------------------
# Latest Change Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import datetime

# Third-party modules
from django import forms
from pymongo import ReadPreference

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.core.mongo.connection import get_db
from noc.sa.models.useraccess import UserAccess
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.profile import Profile
from noc.dns.models.dnszone import DNSZone
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    repo = forms.ChoiceField(
        label=_("Report Type"), choices=[("config", "config"), ("dnszone", "DNS")]
    )
    days = forms.IntegerField(label=_("In Days"), min_value=1)
    adm_domain = forms.ModelChoiceField(
        label=_("Managed Objects Administrative Domain (for config only)"),
        required=False,
        queryset=AdministrativeDomain.objects.order_by("name"),
    )
    managed_object = forms.CharField(
        label=_("Managed object search (for config only)"),
        required=False,
        help_text=_("Use name, network (ex 10.0.0.0/8) or MAC"),
    )


class ReportLatestChangesApplication(SimpleReport):
    title = _("Latest Changes")
    form = ReportForm

    def get_data(
        self, request, repo="config", days=1, adm_domain=None, managed_object=None, **kwargs
    ):
        baseline = datetime.datetime.now() - datetime.timedelta(days=days)
        coll = get_db()["noc.gridvcs.%s.files" % repo].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )
        pipeline = [
            {"$match": {"ts": {"$gte": baseline}}},
            {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
            {"$sort": {"_id": 1}},
        ]
        if repo == "config":
            objects = ManagedObject.objects.filter()
            if not request.user.is_superuser:
                objects = objects.filter(
                    administrative_domain__in=UserAccess.get_domains(request.user)
                )
            if adm_domain:
                adm_domain = AdministrativeDomain.get_nested_ids(adm_domain)
                objects = objects.filter(administrative_domain__in=adm_domain)
            if managed_object:
                mo_q = ManagedObject.get_search_Q(managed_object)
                if not mo_q:
                    objects = objects.filter(name__contains=managed_object)
                else:
                    objects = objects.filter(mo_q)
            pipeline = [
                {"$match": {"object": {"$in": list(objects.values_list("id", flat=True))}}},
                *pipeline,
            ]
        # Perform query
        data = list(coll.aggregate(pipeline))
        # Resolve names
        result = []
        if data:
            seen_ids = list({d["_id"] for d in data})
            n_map = {}
            if repo == "config":
                n_map = {
                    x[0]: x[1:]
                    for x in ManagedObject.objects.filter(id__in=list(seen_ids)).values_list(
                        "id", "name", "address", "profile"
                    )
                }
            elif repo == "dns":
                n_map = {
                    x[0]: x[1:]
                    for x in DNSZone.objects.filter(id__in=list(seen_ids)).values_list(
                        "id", "name", "address", "profile"
                    )
                }
            for d in data:
                name, address, profile = n_map.get(d["_id"], ("-", "-", None))
                result += [
                    (
                        d["_id"],
                        name,
                        address,
                        Profile.get_by_id(profile) if profile else "-",
                        d["last_ts"],
                    )
                ]
        return self.from_dataset(
            title="%s: %s in %d days" % (self.title, repo, days),
            columns=[
                "ID",
                "Name",
                "Address",
                "Profile",
                TableColumn(_("Last Changed"), format="datetime"),
            ],
            data=result,
            enumerate=True,
        )
