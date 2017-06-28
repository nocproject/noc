# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Compact scheduler's collections
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.scheduler.scheduler import Scheduler
from noc.main.models.pool import Pool


def fix():
    for p in Pool.objects.all():
        s = Scheduler("discovery", pool=p.name)
        c = s.get_collection()
        if not c.count():
            continue
        # Remove unused schedules fields
        c.update({
            "jcls": "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"
        }, {
            "$unset": {
                "ctx": "",
                "ctv": ""
            }
        }, multi=True)
        c.database.command({"compact": c.name, "force": True})
