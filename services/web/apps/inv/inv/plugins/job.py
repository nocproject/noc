# ---------------------------------------------------------------------
# inv.inv job plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Iterable, Tuple, Dict, DefaultDict, Any, Set
from collections import defaultdict

# Third party modules
from bson import ObjectId

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from noc.core.hash import hash_int
from noc.sa.models.job import Job
from .base import InvPlugin


class JobPlugin(InvPlugin):
    name = "job"
    js = "NOC.inv.inv.plugins.job.JobPanel"

    def init_plugin(self):
        super().init_plugin()

    def get_data(self, request, obj: Object):
        if obj.is_xcvr and obj.parent and obj.parent_connection:
            root = obj.parent.as_resource(obj.parent_connection)
        else:
            root = obj.as_resource()
        # Get jobs
        jobs = {
            job.id: job
            for job in Job.objects.filter(resource_path=root).order_by("-id").limit(1_000)
        }
        r = [
            {
                "id": str(job.id),
                "name": job.name,
                "description": job.description,
                "created_at": str(job.created_at) if job.created_at else None,
                "completed_at": str(job.completed_at) if job.completed_at else None,
                "status": job.status,
            }
            for job in jobs.values()
            if not job.parent or job.parent.id not in jobs
        ]
        return {"data": r}
