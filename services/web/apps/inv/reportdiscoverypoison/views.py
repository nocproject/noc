# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.inv.models.discoveryid import DiscoveryID
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    pool = forms.ChoiceField(
        label=_("Pool"),
        required=False,
        initial=None,
        choices=[(x, x) for x in Pool.objects.order_by("name").scalar("name")] + [(None, "-")],
    )


class ReportDiscoveryIDPoisonApplication(SimpleReport):
    title = _("Discovery ID cache poison")
    form = ReportForm

    def get_data(self, request, pool=None, **kwargs):

        data = []
        # Find object with equal ID
        find = DiscoveryID._get_collection().aggregate(
            [{"$group": {"_id": "$macs", "count": {"$sum": 1}}}, {"$match": {"count": {"$gt": 1}}}]
        )

        for f in find:
            # DiscoveryID.objects.filter(chassis_mac=f["_id"])
            if not f["_id"]:
                # Empty DiscoveryID
                continue
            data_c = []
            pool_c = set()
            reason = "Other"

            for r in DiscoveryID._get_collection().find(
                {"macs": f["_id"][0]}, {"_id": 0, "object": 1}
            ):
                # ManagedObject.get_by_id(o)
                mo = ManagedObject.get_by_id(r["object"])
                if len(data_c) > 0:
                    if mo.address == data_c[-1][1]:
                        reason = _("Duplicate MO")
                    elif not mo.is_managed == data_c[-1][4]:
                        reason = _("MO is move")
                pool_c.add(mo.pool.name)
                data_c.append((mo.name, mo.address, mo.profile.name, mo.pool.name, mo.is_managed))
            if pool and pool not in pool_c:
                continue
            data += [SectionRow(name="%s %s" % (f["_id"][0], reason))]
            data += data_c

        return self.from_dataset(
            title=self.title,
            columns=[_("Managed Object"), _("Address"), _("Profile"), _("Pool"), _("is managed")],
            data=data,
        )
