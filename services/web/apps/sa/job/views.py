# ----------------------------------------------------------------------
# sa.job application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.sa.models.job import Job
from noc.core.translation import ugettext as _


class JobApplication(ExtDocApplication):
    """
    Job application
    """

    title = _("Jobs")
    menu = [_("Jobs")]
    model = Job
    glyph = "truck"

    @view("^(?P<id>[0-9a-f]{24})/viz/$", access="read")
    def view_viz(self, request, id: str):
        job = self.get_object_or_404(Job, id=id)
        return self.get_viz(job)

    @staticmethod
    def get_viz(job: Job) -> dict[str, Any]:
        """
        Generate Viz scheme for job.
        """
        return {
            "graphAttributes": {"directed": True, "rankdir": "LR"},
            "nodes": [{"name": f"job-{job.id}", "attributes": {"shape": "box", "label": job.name}}],
            "edges": [],
            "subgraphs": [],
        }
