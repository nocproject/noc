# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.reportdiscovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.inv.models.discoveryid import DiscoveryID
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ReportDiscoveryIDPoisonApplication(SimpleReport):
    title = _("Discovery ID cache poison")

    def get_data(self, request, **kwargs):

        data = []
        # Find object with equal ID
        find = DiscoveryID._get_collection().aggregate([
            {"$group": {
                "_id": "$macs",
                "count": {"$sum": 1}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ])

        for f in find:
            # DiscoveryID.objects.filter(chassis_mac=f["_id"])
            if not f["_id"]:
                # Empty DiscoveryID
                continue
            data_c = []
            reason = "Other"

            for r in DiscoveryID._get_collection().find({
                "macs": f["_id"][0]
            }, {"_id": 0, "object": 1}):
                # ManagedObject.get_by_id(o)
                mo = ManagedObject.get_by_id(r["object"])
                if len(data_c) > 0:
                    if mo.address == data_c[-1][1]:
                        reason = _("Duplicate MO")
                    elif not mo.is_managed == data_c[-1][3]:
                        reason = _("MO is move")

                data_c += [(
                    mo.name,
                    mo.address,
                    mo.profile.name,
                    mo.is_managed
                )]

            data += [SectionRow(name="%s %s" % (f["_id"][0], reason))]
            data += data_c

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"),
                _("Profile"), _("is managed")
            ],
            data=data)
