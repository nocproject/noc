# ---------------------------------------------------------------------
# Fix suspended jobs
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool


def fix():
    print("Scanning ...")
    for p in Pool.objects.all():
        print(f"\npool [{p.name}] ...")
        sched = Scheduler("discovery", pool=p.name)

        keys = []
        for job in sched.get_collection().aggregate(
            [{"$match": {Job.ATTR_STATUS: Job.S_SUSPEND}}, {"$group": {"_id": f"${Job.ATTR_KEY}"}}]
        ):
            mo_id = job.get("_id")
            if not mo_id:
                continue

            mo = ManagedObject.get_by_id(mo_id)
            if not (mo.get_status() and mo.object_profile.enable_ping and mo.is_managed):
                continue
            keys.append(mo_id)

        print(f"pool [{p.name}] has [{len(keys)}] online objects with suspended jobs")
        if keys:
            print("Fix suspended state for jobs ...")
            sched.suspend_keys(keys=keys, suspend=False)
