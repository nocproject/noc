# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.monitor application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python module
import re
import zlib
#  # NOC modules
from noc.lib.nosql import get_db
from noc.services.web.apps.sa.objectlist.views import ObjectListApplication
from noc.lib.dateutils import humanize_distance
from noc.core.scheduler.scheduler import Scheduler
from noc.core.scheduler.job import Job
from noc.main.models.pool import Pool
from noc.core.translation import ugettext as _
from noc.lib.app.modelapplication import ModelApplication


class MonitorApplication(ObjectListApplication):
    """
    sa.monitor application
    """
    title = _("Monitor")
    menu = _("Monitor")
    icon = "icon_monitor"

    rx_time = re.compile(r"Completed. Status: SUCCESS\s\((?P<time>\S+)\)", re.MULTILINE)

    def get_job_data(self, scheduler, pool=None, status=None, key=None, jcls=None):
        result = []
        scheduler = Scheduler(
            name=scheduler,
            pool=pool,
        )
        if status:
            q = {"s": status}
        if key:
            q = {"jcls": jcls, "key": key}
        for r in scheduler.get_collection().find(q):
            res = r["key"]
            result.append(res)
        return result

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        print request
        "----------"
        print query
        status = request.POST.get("status")
        if not status:
            status = "R"
        self.logger.info("Queryset %s" % query)
        res = []
        for p in Pool.objects.filter():
            if p.name == "P0001":
                continue
            res += self.get_job_data("discovery", pool=p.name, status=status)
        return self.model.objects.filter(id__in=res)

    def get_data(self, job, job_key, prefix, mo_id):
        time = '--'
        last_success = humanize_distance(job["last"]) if "last" in job else '--'
        last_status = job.get(Job.ATTR_LAST_STATUS)
        time_start = self.to_json(job.get(Job.ATTR_TS))
        status = job["s"] if "s" in job else '--'
        if status == Job.S_WAIT:
            key = "discovery-%s-%s" % (job_key, mo_id)
            joblog = get_db()["noc.joblog"].find_one({"_id": key})
            if joblog and joblog.get("log"):
                res = ModelApplication.render_plain_text(zlib.decompress(str(joblog.get("log"))))
                match = self.rx_time.search(str(res))
                if match:
                    s = match.group("time").split(".")[0]
                    if len(s) > 3:
                        time = "%s sec" % (int(s) / 1000)
                    else:
                        time = "%s mc" % s
        return {
            '%s_time_start' % prefix: time_start,
            '%s_last_success' % prefix: last_success,
            '%s_status' % prefix: status,
            '%s_time' % prefix: time,
            '%s_duration' % prefix: "",
            '%s_last_status' % prefix: last_status,
        }

    def instance_to_dict(self, mo, fields=None):

        result = {
            'id': str(mo.id),
            'name': mo.name,
            'address': mo.address,
            'profile_name': mo.profile.name
        }
        box_jcls = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
        periodic_jcls = "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"

        box_job = Job.get_job_data("discovery",
                                   jcls=box_jcls,
                                   key=mo.id,
                                   pool=mo.pool.name
                                   )

        periodic_job = Job.get_job_data("discovery",
                                        jcls=periodic_jcls,
                                        key=mo.id,
                                        pool=mo.pool.name
                                        )

        if box_job:
            res = self.get_data(box_job, box_jcls, "b", mo.id)
            result.update(res)
        if periodic_job:
            res = self.get_data(periodic_job, periodic_jcls, "p", mo.id)
            result.update(res)
        return result
