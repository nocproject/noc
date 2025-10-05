# ---------------------------------------------------------------------
# sa.groupaccess application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.apps.sa.objectlist.views import ObjectListApplication
from noc.core.dateutils import humanize_distance
from noc.core.scheduler.job import Job
from noc.core.translation import ugettext as _


class GetNowApplication(ObjectListApplication):
    """
    sa.getnow application
    """

    title = _("Get Now")
    menu = _("Get Now")
    icon = "icon_monitor"

    def instance_to_dict(self, mo, fields=None):
        job = Job.get_job_data(
            "discovery",
            jcls="noc.services.discovery.jobs.box.job.BoxDiscoveryJob",
            key=mo.id,
            pool=mo.pool.name,
        )
        last_update = mo.config.get_revisions(reverse=True)
        if last_update:
            last_update = humanize_distance(last_update[0].ts)
        last_success = "--"
        last_status = None
        if job:
            last_success = humanize_distance(job["last"]) if "last" in job else "--"
            last_status = job.get("ls", None)
        return {
            "id": str(mo.id),
            "name": mo.name,
            "profile_name": mo.profile.name,
            "last_success": last_success,
            "status": job["s"] if job else "--",
            "last_status": last_status,
            "last_update": last_update if last_update else None,
        }
