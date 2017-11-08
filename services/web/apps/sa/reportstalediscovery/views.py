# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Stale Discovery Job Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

from noc.core.scheduler.scheduler import Scheduler
from noc.core.translation import ugettext as _
# Django modules
# NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.lib.dateutils import humanize_distance
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject


class ReportStaleDiscoveryJob(SimpleReport):
    title = _("Stale discovery")

    # Minutes
    STALE_INTERVAL = 24 * 60 * 2

    def get_data(self, **kwargs):
        old = datetime.datetime.now() - \
              datetime.timedelta(minutes=self.STALE_INTERVAL)
        data = []
        for pool in Pool._get_collection().find({},
                                                {"_id": 0, "name": 1}):
            scheduler = Scheduler("discovery", pool=pool["name"])
            for r in scheduler.get_collection().find({
                "runs": {
                    "$gt": 1
                },
                "jcls": {
                    "$regex": "_discovery$"
                },
                "st": {
                    "$lte": old
                }
            }):
                mo = ManagedObject.get_by_id(r["key"])
                if not mo or not mo.is_managed:
                    continue
                msg = ""
                if r["tb"]:
                    tb = r["tb"]
                    if "text" in tb and "code" in tb:
                        if tb["text"].endswith("END OF TRACEBACK"):
                            tb["text"] = "Job crashed"
                        msg = "(%s) %s" % (tb["text"], tb["code"])
                data += [[
                    mo.administrative_domain.name,
                    mo.name,
                    mo.profile.name,
                    mo.platform.name,
                    mo.version.name,
                    mo.address,
                    mo.segment.name,
                    r["jcls"],
                    humanize_distance(r["st"]),
                    msg
                ]]
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Admin. Domain"),
                _("Object"),
                _("Profile"),
                _("Platform"),
                _("Version"),
                _("Address"),
                _("Segment"),
                _("Job"),
                _("Last Success"),
                _("Reason")
            ],
            data=sorted(data),
            enumerate=True)
