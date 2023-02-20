# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, SectionRow
from noc.inv.models.discoveryid import DiscoveryID
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _
from noc.core.mac import MAC
from noc.inv.models.macblacklist import MACBlacklist


class ReportForm(forms.Form):
    pool = forms.ChoiceField(
        label=_("Pool"),
        required=False,
        initial=None,
        choices=[(x, x) for x in Pool.objects.order_by("name").scalar("name")] + [(None, "-")],
    )
    filter_dup_macs = forms.BooleanField(label=_("Exclude on MAC Black List"), required=False)


class ReportDiscoveryIDPoisonApplication(SimpleReport):
    title = _("Discovery ID cache poison")
    form = ReportForm

    def get_data(self, request, pool=None, filter_dup_macs=False, **kwargs):
        data = []
        # Find object with equal ID
        find = DiscoveryID._get_collection().aggregate(
            [
                {"$unwind": "$macs"},
                {"$group": {"_id": "$macs", "count": {"$sum": 1}, "mo": {"$push": "$object"}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$group": {"_id": "$mo", "macs": {"$push": "$_id"}}},
                {"$project": {"macs": 1, "smacs": {"$arrayElemAt": ["$macs", 0]}}},
                {"$sort": {"smacs": 1}},
            ],
            allowDiskUse=True,
        )

        for f in find:
            # DiscoveryID.objects.filter(chassis_mac=f["_id"])
            if not f["_id"]:
                # Empty DiscoveryID
                continue
            data_c = []
            pool_c = set()
            reason = "Other"
            for mo in sorted(ManagedObject.objects.filter(id__in=f["_id"]), key=lambda x: x.name):
                pool_c.add(mo.pool.name)
                data_c.append((mo.name, mo.address, mo.profile.name, mo.pool.name, mo.is_managed))
            if len(data_c) > 0:
                if data_c[0][1] == data_c[1][1]:
                    reason = _("Duplicate MO")
                elif not data_c[0][4] == data_c[1][4]:
                    reason = _("MO is move")
            if pool and pool not in pool_c:
                continue
            if reason == "Other" and MACBlacklist.is_banned_mac(f["macs"][0], is_duplicated=True):
                if filter_dup_macs:
                    continue
                data += [
                    SectionRow(name="%s %s (%s)" % (MAC(f["macs"][0]), reason, "On duplicated"))
                ]
            else:
                data += [SectionRow(name="%s %s" % (MAC(f["macs"][0]), reason))]
            data += data_c

        return self.from_dataset(
            title=self.title,
            columns=[_("Managed Object"), _("Address"), _("Profile"), _("Pool"), _("is managed")],
            data=data,
        )
