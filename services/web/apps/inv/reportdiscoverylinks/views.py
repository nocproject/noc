# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Report Discovery Link Summary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport, SectionRow
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.profile import Profile
from noc.core.translation import ugettext as _
from noc.core.profile.loader import GENERIC_PROFILE


class ReportFilterApplication(SimpleReport):
    title = _("Discovery Links Summary")
    predefined_reports = {
        "default": PredefinedReport(
            _("Discovery Links Summary"), {}
        )
    }

    def get_data(self, request, **kwargs):
        data = []

        value = get_db()["noc.links"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate(
            [
                {"$unwind": "$interfaces"},
                {
                    "$lookup": {
                        "from": "noc.interfaces",
                        "localField": "interfaces",
                        "foreignField": "_id",
                        "as": "int"
                    }
                },
                {"$group": {"_id": "$int.managed_object", "count": {"$sum": 1}}}
            ])
        count = {0: set([]), 1: set([]), 2: set([]), 3: set([])}
        ap = AuthProfile.objects.filter(name__startswith="TG")
        for v in value:
            if v["count"] > 2:
                count[3].add(v["_id"][0])
                continue
            if not v["_id"]:
                self.logger.warning("No IDS in response query")
                continue
            count[v["count"]].add(v["_id"][0])

        for p in Pool.objects.order_by("name"):
            if p.name == "P0001":
                continue
            data += [SectionRow(name=p.name)]
            smos = set(
                ManagedObject.objects.filter(
                    pool=p, is_managed=True).exclude(
                    profile=Profile.get_by_name(GENERIC_PROFILE)).exclude(
                    auth_profile__in=ap
                ).values_list('id', flat=True))
            all_p = 100.0/len(smos) if len(smos) else 1.0
            data += [("All polling", len(smos))]
            for c in count:
                if c == 3:
                    data += [("More 3", len(count[c].intersection(smos)), "%.2f %%" %
                              round(len(count[c].intersection(smos))*all_p, 2))]
                    continue
                data += [(c, len(count[c].intersection(smos)), "%.2f %%" % round(len(count[c].intersection(smos))*all_p), 2)]

            # 0 links - All discovering- summary with links
            s0 = len(smos) - sum([d[1] for d in data[-3:]])
            data.pop(-4)
            data.insert(-3, (0, s0, "%.2f %%" % round(s0*all_p, 2)))

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Links count"), _("MO Count"), _("Percent at All")
            ],
            data=data)
