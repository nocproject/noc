# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Stale Discovery Job Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.lib.nosql import get_db
from noc.lib.dateutils import humanize_distance
from noc.sa.models import ManagedObject


class ReportStaleDiscoveryJob(SimpleReport):
    title = "Stale discovery"

    # Minutes
    STALE_INTERVAL = 24 * 60 * 2

    def get_data(self, **kwargs):
        old = datetime.datetime.now() - \
              datetime.timedelta(minutes=self.STALE_INTERVAL)
        s = get_db()["noc.schedules.inv.discovery"]
        data = []
        for r in s.find(
                {"runs": {"$gt": 1},
                 "jcls": {'$regex': '_discovery$'},
                 "st": {"$gte": old}}
        ).sort("jcls"):
            mo = ManagedObject.objects.get(id=r['key'])
            msg = ""
            if r["tb"]:
                tb = r["tb"]
                if "text" in tb and "code" in tb:
                    if tb["text"].endswith("END OF TRACEBACK"):
                        tb["text"] = "Job crashed"
                    msg = "(%s) %s" % (tb["text"], tb["code"])

            if mo.name == "SAE":
                continue
            data += [[
                         mo.administrative_domain.name,
                         mo.name,
                         mo.profile_name,
                         mo.platform,
                         mo.address,
                         r['jcls'],
                         humanize_distance(r["st"]),
                         msg
                     ]]
        return self.from_dataset(
            title=self.title,
            columns=[
                "Admin. Domain",
                "Object",
                "Profile",
                "Platform",
                "Address",
                "Script",
                "Last Success",
                "Reason"
            ],
            data=sorted(data),
            enumerate=True)
