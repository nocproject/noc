# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportdiscovery
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
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
                "_id": "$chassis_mac",
                "count": {"$sum": 1}
                }},
            {"$match": {"count": {"$gt": 1}}}
        ])

        for f in find["result"]:
            # DiscoveryID.objects.filter(chassis_mac=f["_id"])
            if not f["_id"]:
                # Empty DiscoveryID
                continue
            data += [SectionRow(name=f["_id"][0])]
            reason = "Other"
            prev_mo = None
            for r in DiscoveryID._get_collection().find({
                "chassis_mac": {
                    "$elemMatch": f["_id"][0]
                }
            }, {"_id": 0, "object": 1}):
                # ManagedObject.get_by_id(o)
                mo = ManagedObject.get_by_id(r["object"])
                if prev_mo == mo.address:
                    reason = "Duplicate MO"
                    d = data.pop()
                    data += [(
                        d[0], d[1], d[2], reason
                    )]

                data += [(
                    mo.name,
                    mo.address,
                    mo.profile.name,
                    reason
                )]
                prev_mo = mo.address

        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Address"),
                _("Profile"), _("Error")
            ],
            data=data)
