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
    # <State: ManagedObject Default: Managed>
    managed_state = State.objects.filter(id="641b35e6fa01fd032a1f61f1").first()

    for p in Pool.objects.all():
        print(f"Processing pool {p.name}")
        sched = Scheduler("discovery", pool=p.name)

        keys = []
        for job in sched.get_collection().aggregate(
            [{"$match": {Job.ATTR_STATUS: Job.S_SUSPEND}}, {"$group": {"_id": f"${Job.ATTR_KEY}"}}]
        ):
            # print("Job", job)
            mo_id = job.get("_id")
            if mo_id:
                mo = ManagedObject.get_by_id(mo_id)
                if not (
                    mo.get_status() and mo.object_profile.enable_ping and mo.state == managed_state
                ):
                    continue
                keys.append(mo_id)

        print(f"pool {p.name} has {len(keys)} bad objects")
        for x in keys[0:5]:
            print(x)
        if keys:
            print("Fix suspended state for jobs")
            sched.suspend_keys(keys=keys, suspend=False)
