# ---------------------------------------------------------------------
# Escalation Runner implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Dict, Any

# NOC modules
from noc.core.runner.runner import Runner
from noc.services.escalator.job import AlarmAutomationJob
from noc.core.tt.types import EscalationRequest


class EscalationRunner(Runner):

    def _save_new_job(self, job: AlarmAutomationJob, req: EscalationRequest) -> None:
        """
        Send to persistent storage.
        """
        if not self._queue:
            return
        r: Dict[str, Any] = {
            "_id": job.id,
            "name": req.name,
            "parent": job.parent.id if job.parent else None,
            "description": req.description,
            "allow_fail": req.allow_fail,
            "status": job.status.value,
            "action": req.action or None,
            "inputs": (
                [{"name": i.name, "value": i.value, "job": i.job} for i in req.inputs]
                if req.inputs
                else None
            ),
            "locks": req.locks,
            "depends_on": [j.id for j in job.iter_depends_on()],
            "environment": req.environment or None,
            "created_at": datetime.datetime.now(),
            "resource_path": req.resource_path,
            "entity": req.entity,
        }
        self._queue.put_nowait((None, r))
